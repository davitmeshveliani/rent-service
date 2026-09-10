"""
Serializers for user domain including registration, profile management,
password updates, and token revocation.
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration.
    Delegates user domain validation rules directly to User.full_clean().
    Newly registered users are automatically assigned to the GUEST Django Group.
    """

    password = serializers.CharField(write_only=True,required=True,validators=[validate_password],)
    email = serializers.EmailField(required=True,
                                error_messages={"invalid": "Please enter a valid email address.",
                                                    "blank": "Email field cannot be blank.",},)

    class Meta:
        model = User
        fields = ("id","username","email","password","phone_number","first_name",
                                            "last_name","birthday","address","gender","bio",)

    @staticmethod
    def validate_username(value: str) -> str:
        """Ensure that the provided username is unique across the system."""
        cleaned_username = value.strip()
        if User.objects.filter(username__iexact=cleaned_username).exists():
            raise serializers.ValidationError("This username is already taken.")
        return cleaned_username

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Delegate domain attributes validation to Model clean()."""
        # Exclude write-only password from instance dry-run
        data_for_clean = {k: v for k, v in attrs.items() if k != "password"}


        instance = User(**data_for_clean)
        instance.set_password(attrs["password"])

        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Create a new user and assign the GUEST group."""
        user = User.objects.create_user(**validated_data)
        guest_group, _ = Group.objects.get_or_create(name="GUEST")
        user.groups.add(guest_group)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating user profile details.
    Delegates attribute validation directly to User.full_clean().
    """

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("id","username","email","phone_number","first_name",
                                    "last_name","birthday","address","gender","bio","is_active",)

        read_only_fields = ("id","username" ,"is_active",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Delegate instance updates validation to Model clean()."""
        for attr, value in attrs.items():
            setattr(self.instance, attr, value)
        try:
            self.instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing the authenticated user's password.
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True,validators=[validate_password],)

    def validate_old_password(self, value: str) -> str:
        """Validate that the old password matches the current password."""
        user: Any = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Ensure that the new password differs from the old password."""
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "The new password cannot be the same as the old password."})
        return attrs


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for validating and blacklisting refresh tokens during logout.
    """

    refresh = serializers.CharField(required=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.token: str | None = None

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Store the raw refresh token for processing during save."""
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs: Any) -> None:
        """Blacklist the refresh token to revoke future access."""
        if not self.token:
            raise serializers.ValidationError({"refresh": "Token is required."})
        try:
            token = RefreshToken(self.token)  # type: ignore[arg-type]
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError({"refresh": "Invalid or expired token."})