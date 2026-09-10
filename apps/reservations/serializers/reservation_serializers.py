"""
Serializers for reservation creation, management, and status updates.
"""

from typing import Any, ClassVar

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

ReservationModel: Any = apps.get_model("reservations", "Reservation")


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving reservation data.
    Delegates domain validation rules directly to Reservation.full_clean().
    """

    user = serializers.StringRelatedField(read_only=True)
    listing_title = serializers.ReadOnlyField(source="listing.title")

    class Meta:
        model = ReservationModel
        fields: ClassVar[list[str]] = ["id","listing","listing_title","user",
                                     "status","start_date","end_date","created_at",]

        read_only_fields: ClassVar[list[str]] = ["id", "user", "status", "created_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # 1. Authentication check
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication required."})

        # 2. Build instance for validation
        if self.instance:
            instance = ReservationModel(
                                    pk=self.instance.pk,
                                    listing=attrs.get("listing", self.instance.listing),
                                    user=self.instance.user,
                                    status=attrs.get("status", self.instance.status),
                                    start_date=attrs.get("start_date", self.instance.start_date),
                                    end_date=attrs.get("end_date", self.instance.end_date),
                                    is_deleted=self.instance.is_deleted,)
        else:
            instance = ReservationModel(user=user,**attrs,)


        # 3. Delegate business rules to Model clean()
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs


class ReservationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for reservation status updates.
    Enforces host and guest authorization logic during status transition.
    """

    class Meta:
        model = ReservationModel
        fields: ClassVar[list[str]] = ["status"]

    def validate_status(self, value: str) -> str:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        reservation = self.instance

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        if reservation is None:
            raise serializers.ValidationError("Reservation is required.")

        current_status = reservation.status
        is_host = reservation.listing.user_id == user.id
        is_guest = reservation.user_id == user.id

        # Host actions
        if is_host:
            if current_status != ReservationModel.StatusChoice.PENDING:
                raise serializers.ValidationError("Only pending reservations can be confirmed or rejected.")

            allowed_statuses = {ReservationModel.StatusChoice.CONFIRMED,ReservationModel.StatusChoice.REJECTED,}
            if value not in allowed_statuses:
                raise serializers.ValidationError("Hosts can only confirm or reject pending reservations.")
            return value

        # Guest actions
        if is_guest:
            if value != ReservationModel.StatusChoice.CANCELLED:
                raise serializers.ValidationError("Guests can only cancel their reservation.")

            if current_status not in {ReservationModel.StatusChoice.PENDING,ReservationModel.StatusChoice.CONFIRMED,}:
                raise serializers.ValidationError(
                    "Only pending or confirmed reservations can be cancelled.")

            if reservation.start_date <= timezone.now():
                raise serializers.ValidationError("A reservation cannot be cancelled after the start date.")
            return value

        # Unauthorized user
        raise serializers.ValidationError("You do not have permission to update this reservation.")