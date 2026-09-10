from typing import Any
from django.utils import timezone
from django.db.models import QuerySet

from apps.reservations.models import Reservation
from apps.reservations.repositories.reservation_repository import (ReservationRepository,)


class ReservationService:
    def __init__(self) -> None:
        self.repository = ReservationRepository()


    def get_all_user_reservations(self,user: Any,) -> QuerySet[Reservation]:
        return self.repository.get_user_related_reservations(user)


    def get_guest_reservations(self,user: Any,) -> QuerySet[Reservation]:
        return self.repository.get_guest_reservations(user)


    def get_host_reservations(self,user: Any,) -> QuerySet[Reservation]:
        return self.repository.get_host_reservations(user)


    def cancel_reservation(self,reservation: Reservation,user: Any,) -> bool:
        if reservation.user != user:
            return False
        self.repository.cancel_reservation(reservation)
        return True


    def update_status(self,reservation: Reservation,user: Any,new_status: str,) -> bool:
        """
        Apply valid reservation status transitions.

        Host:
            PENDING -> CONFIRMED
            PENDING -> REJECTED

        Guest:
            PENDING/CONFIRMED -> CANCELLED
            only before the start date.
        """

        current_status = reservation.status

        is_host = reservation.listing.user == user
        is_guest = reservation.user == user

        if is_host:
            if current_status != Reservation.StatusChoice.PENDING:
                return False
            if new_status not in {
                                Reservation.StatusChoice.CONFIRMED,
                                Reservation.StatusChoice.REJECTED,}:
                return False
        elif is_guest:
            if new_status != Reservation.StatusChoice.CANCELLED:
                return False

            if current_status not in {
                Reservation.StatusChoice.PENDING,Reservation.StatusChoice.CONFIRMED,}:
                return False
            if reservation.start_date <= timezone.now():
                return False
        else:
            return False
        self.repository.update_status(reservation, new_status)
        return True