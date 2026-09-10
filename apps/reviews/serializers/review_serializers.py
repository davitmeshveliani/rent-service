"""
Serializers for review creation and management with reservation checks.
"""

from typing import Any

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving reviews.
    Delegates model constraints to Review.full_clean() and verifies stay completion.
    """

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "listing", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "user", "created_at"]



    @staticmethod
    def validate_comment(value: str | None) -> str | None:
        """Ensure comment meets minimum character length requirements."""
        if not value:
            return value

        cleaned_comment = value.strip()
        if cleaned_comment and len(cleaned_comment) < 10:
            raise serializers.ValidationError(
                "Comment must be at least 10 characters long.")

        return cleaned_comment

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication required."})

        # Check for finished reservation prior to review creation

        if not self.instance:
            listing = attrs.get("listing")
            reservation_model = apps.get_model("reservations", "Reservation")

            has_valid_reservation = reservation_model.objects.filter(
                user=user,listing=listing,status=reservation_model.StatusChoice.CONFIRMED,
                                            end_date__lt=timezone.now(),).exists()

            if not has_valid_reservation:
                raise serializers.ValidationError(
                    {"listing":
                         ("You can only review a listing after "
                          "completing a confirmed stay.")})

        # Build / update instance and delegate to Model clean()

        if self.instance:
            for attr, val in attrs.items():
                setattr(self.instance, attr, val)
            instance = self.instance
        else:
            instance = Review(user=user, **attrs)
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs