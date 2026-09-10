"""
Reservation domain model representing property bookings.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from apps.core.models import UUIDAbstractModel
from apps.listings.models import Apartment


class Reservation(UUIDAbstractModel):
    """
    Model representing an apartment booking/reservation.
    """

    objects = models.Manager()

    class StatusChoice(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    listing = models.ForeignKey(Apartment,on_delete=models.CASCADE,related_name="reservations",)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reservations",)
    status = models.CharField(max_length=20,choices=StatusChoice.choices,default=StatusChoice.PENDING,)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reservations"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gt=F("start_date")),
                name="check_reservation_end_date_after_start_date",),]

    def clean(self) -> None:
        super().clean()

        if not self.start_date or not self.end_date:
            return

        # 2. end_date

        if self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be strictly after start date."})


        # year + 1
        if self._state.adding and self.start_date < timezone.now():
            raise ValidationError(
                {"start_date": "Reservation start date cannot be in the past."})

        max_start_date = timezone.now() + relativedelta(years=1)

        if self._state.adding and self.start_date > max_start_date:
            raise ValidationError(
                {"start_date": "Reservation cannot be made more than one year in advance."})

        # 4. Guard Clause:

        listing_id = getattr(self, "listing_id", None)
        active_statuses = {self.StatusChoice.PENDING, self.StatusChoice.CONFIRMED}

        if not listing_id or self.is_deleted or self.status not in active_statuses:
            return

        # 5. Overlapping

        overlapping_qs = Reservation.objects.filter(
                                    listing_id=listing_id,
                                    is_deleted=False,
                                    status__in=active_statuses,
                                    start_date__lt=self.end_date,
                                    end_date__gt=self.start_date,)

        if self.pk:
            overlapping_qs = overlapping_qs.exclude(pk=self.pk)

        if overlapping_qs.exists():
            raise ValidationError({"start_date": "This apartment is already reserved for the selected date range."})

    def __str__(self) -> str:
        user_identifier: str = getattr(self.user, "username", str(self.user))
        return f"Reservation {self.id} - {user_identifier} ({self.status})"