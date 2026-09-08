"""
URL routing configuration for the reservations application.
"""

from typing import Any
from django.urls import path

from apps.reservations.controllers.reservation_controllers import (
                                        HostReservationsAPIView,
                                        MyReservationsAPIView,
                                        ReservationCancelAPIView,
                                        ReservationListCreateAPIView,
                                        ReservationRetrieveUpdateDestroyAPIView,)

app_name = "reservations"

urlpatterns: list[Any] = [
    path("", ReservationListCreateAPIView.as_view(), name="reservation-list"),
    path("my/", MyReservationsAPIView.as_view(), name="my-reservations"),
    path("host/", HostReservationsAPIView.as_view(), name="host-reservations"),
    path("<uuid:pk>/",ReservationRetrieveUpdateDestroyAPIView.as_view(),name="reservation-detail",),
    path("<uuid:pk>/cancel/",ReservationCancelAPIView.as_view(),name="reservation-cancel",),]