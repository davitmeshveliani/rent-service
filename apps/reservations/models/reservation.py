"""
Reservation domain model representing property bookings.
"""

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from apps.core.models import UUIDAbstractModel
from apps.listings.models import Apartment


class Reservation(UUIDAbstractModel):
    objects = models.Manager()
    """
    Model representing an apartment booking/reservation.
    """

    class StatusChoice(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    listing = models.ForeignKey(Apartment,on_delete=models.CASCADE,related_name="reservations",)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reservations",)
    status = models.CharField(max_length=20,choices=StatusChoice.choices,default=StatusChoice.PENDING,db_index=True,)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)

    is_deleted = models.BooleanField(default=False,db_index=True,)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reservations"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                            condition=Q(end_date__gt=F("start_date")),
                            name="check_reservation_end_date_after_start_date",),]

    def __str__(self) -> str:
        user_identifier: str = getattr(self.user, "username", str(self.user))
        return f"Reservation {self.id} - {user_identifier} ({self.status})"