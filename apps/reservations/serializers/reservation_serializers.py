"""
Serializers for reservation creation, management, and status updates.
"""

from datetime import time
from typing import Any, ClassVar

from django.apps import apps
from django.utils import timezone
from rest_framework import serializers


ReservationModel: Any = apps.get_model("reservations", "Reservation")


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving reservation data.

    Any authenticated user can create a reservation for another user's
    listing. A user cannot reserve their own listing.
    """

    user = serializers.StringRelatedField(read_only=True)
    listing_title = serializers.ReadOnlyField(source="listing.title")

    class Meta:
        model = ReservationModel
        fields: ClassVar[list[str]] = ["id","listing","listing_title","user",
                                         "status","start_date","end_date","created_at",]

        read_only_fields: ClassVar[list[str]] = ["id","user","status","created_at",]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        start_date = attrs.get("start_date",getattr(self.instance, "start_date", None),)
        end_date = attrs.get("end_date",getattr(self.instance, "end_date", None),)
        listing = attrs.get("listing",getattr(self.instance, "listing", None),)

        request = self.context.get("request")
        user = getattr(request, "user", None)

        # Authentication
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication required."})

        # User cannot reserve their own listing
        if listing and getattr(listing, "user", None) == user:
            raise serializers.ValidationError({"listing": "You cannot reserve your own listing."})

        # Check-in cannot be in the past
        if start_date and start_date < timezone.now():
            raise serializers.ValidationError({"start_date": ("Check-in date and time cannot be in the past.")})

        # Check-in must be exactly 12:00
        if start_date and start_date.time() != time(12, 0):
            raise serializers.ValidationError({"start_date": "Check-in time must be 12:00."})

        # Check-out must be exactly 12:00
        if end_date and end_date.time() != time(12, 0):
            raise serializers.ValidationError({"end_date": "Check-out time must be 12:00."})

        # Check-out must be after check-in
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {"end_date": ("Check-out date must be after check-in date.")})

        # Prevent overlapping active reservations
        if listing and start_date and end_date:
            overlapping = ReservationModel.objects.filter(
                listing=listing,
                status__in=[ReservationModel.StatusChoice.PENDING,ReservationModel.StatusChoice.CONFIRMED,],
                start_date__lt=end_date,end_date__gt=start_date,)

            # Exclude current reservation during update
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError(
                    {"start_date":
                         ("The listing is already reserved ""for the selected dates.")})
        return attrs



class ReservationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for reservation status updates.

    Hosts can confirm or reject pending reservations.
    Guests can cancel their own reservations before the start date.
    """

    class Meta:
        model = ReservationModel
        fields: ClassVar[list[str]] = ["status"]

    def validate_status(self, value: str) -> str:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        reservation = self.instance

        # Authentication
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        if reservation is None:
            raise serializers.ValidationError("Reservation is required.")

        current_status = reservation.status

        is_host = reservation.listing.user == user
        is_guest = reservation.user == user

        # Host actions
        if is_host:
            if current_status != ReservationModel.StatusChoice.PENDING:
                raise serializers.ValidationError(
                    "Only pending reservations can be confirmed ""or rejected.")


            allowed_statuses = {ReservationModel.StatusChoice.CONFIRMED,ReservationModel.StatusChoice.REJECTED,}
            if value not in allowed_statuses:
                raise serializers.ValidationError("Hosts can only confirm or reject pending reservations.")
            return value


        # Guest actions
        if is_guest:
            if value != ReservationModel.StatusChoice.CANCELLED:
                raise serializers.ValidationError("Guests can only cancel their reservation.")

            if current_status not in {ReservationModel.StatusChoice.PENDING,
                                      ReservationModel.StatusChoice.CONFIRMED,}:

                raise serializers.ValidationError("Only pending or confirmed reservations ""can be cancelled.")

            # Reservation cannot be cancelled after check-in time
            if reservation.start_date <= timezone.now():
                raise serializers.ValidationError("A reservation cannot be cancelled "
                                                  "after the start date.")
            return value

        # Other users
        raise serializers.ValidationError( "You do not have permission to update this reservation.")

