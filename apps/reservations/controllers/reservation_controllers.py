"""
API controllers for handling reservation listings, creation, updates, and cancellations.
"""

from typing import Any

from django.db.models import Q, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.reservations.models import Reservation
from apps.reservations.controllers.reservation_schema import (
                                    host_reservations_schema,
                                    my_reservations_schema,
                                    reservation_cancel_schema,
                                    reservation_detail_schema,
                                    reservation_list_create_schema,)
from apps.reservations.serializers import (
                                    ReservationSerializer,
                                    ReservationUpdateSerializer,)


class BaseReservationAPIView:
    """
    Mixin to safely return an empty queryset during Swagger schema generation.
    """

    def is_swagger_fake_view(self) -> bool:
        return getattr(self, "swagger_fake_view", False)


@reservation_list_create_schema
class ReservationListCreateAPIView(BaseReservationAPIView, generics.ListCreateAPIView):
    """
    API view to list user-related reservations or create a new booking request.
    Includes select_related optimizations for associated listing and user data.
    """

    queryset = Reservation.objects.select_related("listing", "user", "listing__user").all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "listing"]

    def get_queryset(self) -> QuerySet[Reservation]:
        if self.is_swagger_fake_view():
            return Reservation.objects.none()  # type: ignore[attr-defined]

        return (
            super()
            .get_queryset()
            .filter(Q(user=self.request.user) | Q(listing__user=self.request.user))
            .distinct()
        )

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(user=self.request.user)


@my_reservations_schema
class MyReservationsAPIView(BaseReservationAPIView, generics.ListAPIView):
    """
    API view to retrieve all reservations placed by the authenticated guest user.
    """

    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self) -> QuerySet[Reservation]:
        if self.is_swagger_fake_view():
            return Reservation.objects.none()  # type: ignore[attr-defined]

        return (
            Reservation.objects.filter(user=self.request.user)
            .select_related("listing", "user")
            .order_by("-created_at")
        )


@host_reservations_schema
class HostReservationsAPIView(BaseReservationAPIView, generics.ListAPIView):
    """
    API view to retrieve all booking requests submitted for the host's listings.
    """

    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self) -> QuerySet[Reservation]:
        if self.is_swagger_fake_view():
            return Reservation.objects.none()  # type: ignore[attr-defined]

        return (
            Reservation.objects.filter(listing__user=self.request.user)
            .select_related("listing", "user")
            .order_by("-created_at")
        )


@reservation_detail_schema
class ReservationRetrieveUpdateDestroyAPIView(
    BaseReservationAPIView, generics.RetrieveUpdateDestroyAPIView
):
    """
    API view to retrieve, update, or cancel a specific reservation instance.
    """

    queryset = Reservation.objects.select_related("listing", "user", "listing__user").all()  # type: ignore[attr-defined]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self) -> QuerySet[Reservation]:
        if self.is_swagger_fake_view():
            return Reservation.objects.none()  # type: ignore[attr-defined]
        return (
            super()
            .get_queryset()
            .filter(Q(user=self.request.user) | Q(listing__user=self.request.user))
            .distinct()
        )

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.request.method in ["PUT", "PATCH"]:
            return ReservationUpdateSerializer
        return ReservationSerializer

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        reservation: Reservation = self.get_object()
        if reservation.listing.user != request.user:
            return Response(
                {"detail": "Only the listing owner can delete this reservation."},
                status=status.HTTP_403_FORBIDDEN,
            )
        reservation.delete()
        return Response(
            {"detail": "Reservation has been successfully deleted."},
            status=status.HTTP_200_OK,
        )


class ReservationCancelAPIView(BaseReservationAPIView, generics.GenericAPIView):
    """
    Action endpoint for quickly cancelling a reservation.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer

    def get_queryset(self) -> QuerySet[Reservation]:
        if self.is_swagger_fake_view():
            return Reservation.objects.none()  # type: ignore[attr-defined]

        return Reservation.objects.select_related("listing", "user", "listing__user")  # type: ignore[attr-defined]

    @reservation_cancel_schema
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        reservation: Reservation = self.get_object()
        if reservation.user != request.user and reservation.listing.user != request.user:
            return Response(
                {"detail": "You do not have permission to cancel this reservation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        reservation.status = Reservation.StatusChoice.CANCELLED
        reservation.save(update_fields=["status"])
        return Response(
            {"detail": "Reservation has been successfully cancelled."},
            status=status.HTTP_200_OK,
        )