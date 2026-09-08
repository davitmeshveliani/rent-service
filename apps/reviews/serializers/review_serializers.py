"""
Serializers for review creation and management with reservation checks.
"""

from typing import Any, ClassVar

from django.apps import apps
from django.utils import timezone
from rest_framework import serializers

from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving reviews.

    A user can leave a review only if they have a confirmed
    reservation for the listing and the stay has already ended.
    """

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields: ClassVar[list[str]] = [
                                        "id","listing","user",
                                        "rating","comment","created_at",
                                        ]
        read_only_fields: ClassVar[list[str]] = [
                                                "id","user","created_at",]


    # Field-Level Validations

    @staticmethod
    def validate_rating(value: int) -> int:
        """Ensure rating stays within 1 to 5 stars."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value

    @staticmethod
    def validate_comment(value: str | None) -> str | None:
        """Ensure comment meets minimum character length requirements."""
        if not value:
            return value

        cleaned_comment = value.strip()

        if cleaned_comment and len(cleaned_comment) < 10:
            raise serializers.ValidationError("Comment must be at least 10 characters long.")

        return cleaned_comment

    # Object-Level Validation

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        listing = attrs.get("listing",getattr(self.instance, "listing", None),)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication required."})

        # Reservation and duplicate-review validation only on creation
        if not self.instance:
            reservation_model = apps.get_model("reservations","Reservation",)

            has_valid_reservation = reservation_model.objects.filter(
                                        user=user,
                                        listing=listing,
                                        status=reservation_model.StatusChoice.CONFIRMED,
                                        end_date__lt=timezone.now(),).exists()

            if not has_valid_reservation:
                raise serializers.ValidationError(
                    {
                        "listing": (
                            "You can only review a listing after "
                            "completing a confirmed stay.")})

            if Review.objects.filter(
                user=user,
                listing=listing,).exists():
                raise serializers.ValidationError(
                    {
                        "listing": (
                            "You have already submitted a review "
                            "for this listing.")})
        return attrs