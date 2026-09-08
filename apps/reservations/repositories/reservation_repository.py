from typing import Any
from django.db.models import Q, QuerySet
from apps.reservations.models import Reservation


class ReservationRepository:
    def get_user_related_reservations(self,user: Any,) -> QuerySet[Reservation]:
        return (Reservation.objects.filter(Q(user=user) | Q(listing__user=user)).select_related
                                    ("listing","user","listing__user",).distinct())

    def get_guest_reservations(self,user: Any,) -> QuerySet[Reservation]:
        return (Reservation.objects.filter(user=user).select_related
                ("listing", "user").order_by("-created_at"))

    def get_host_reservations(self,user: Any,) -> QuerySet[Reservation]:
        return (Reservation.objects.filter(listing__user=user).select_related
                             ("listing", "user").order_by("-created_at"))

    def update_status(self,reservation: Reservation,status_value: str,) -> Reservation:
        reservation.status = status_value
        reservation.save(update_fields=["status"])
        return reservation

    def cancel_reservation(self,reservation: Reservation,) -> Reservation:
        return self.update_status(reservation,Reservation.StatusChoice.CANCELLED,)