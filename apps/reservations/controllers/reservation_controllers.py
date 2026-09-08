"""
API views for handling reservation listings, creation, updates, and cancellations.
"""

from typing import Any

from django.db.models import Q, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.reservations.models import Reservation
from apps.reservations.serializers import (
    ReservationSerializer,
    ReservationUpdateSerializer,
)


class BaseReservationAPIView:
    """
    Mixin to safely return an empty queryset during Swagger schema generation.
    """

    def is_swagger_fake_view(self) -> bool:
        return getattr(self, "swagger_fake_view", False)


@extend_schema_view(
    get=extend_schema(
        summary="List user-related reservations",
        description="Retrieves all reservations where the authenticated user is either the guest or the host.",
    ),
    post=extend_schema(
        summary="Create a new reservation",
        description="Guest creates a booking request for a listing.",
    ),
)
class ReservationListCreateAPIView(BaseReservationAPIView, generics.ListCreateAPIView):
    """
    API view to list user-related reservations or create a new booking request.
    Includes select_related optimizations for associated listing and user data.
    """

    # noinspection PyUnresolvedReferences
    queryset = Reservation.objects.select_related("listing", "user", "listing__user").all()  # type: ignore[attr-defined]
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


@extend_schema(
    summary="List guest's own reservations",
    description="Retrieves all reservations booked by the authenticated guest user.",
)
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

        # noinspection PyUnresolvedReferences
        return (
            Reservation.objects.filter(user=self.request.user)  # type: ignore[attr-defined]
            .select_related("listing", "user")
            .order_by("-created_at")
        )


@extend_schema(
    summary="List host's incoming reservation requests",
    description="Retrieves all booking requests for listings owned by the authenticated host.",
)
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

        # noinspection PyUnresolvedReferences
        return (
            Reservation.objects.filter(listing__user=self.request.user)  # type: ignore[attr-defined]
            .select_related("listing", "user")
            .order_by("-created_at")
        )


@extend_schema_view(
    get=extend_schema(
                    summary="Retrieve a reservation",
                    responses={200: ReservationSerializer},),
    put=extend_schema(
                        summary="Update a reservation",
                        request=ReservationUpdateSerializer,
                        responses={200: ReservationSerializer},
                        operation_id="reservations_update",),
    patch=extend_schema(
                        summary="Partial update a reservation",
                        request=ReservationUpdateSerializer,
                        responses={200: ReservationSerializer},
                        operation_id="reservations_partial_update",),
    delete=extend_schema(summary="Delete a reservation",responses={204: None},),)
class ReservationRetrieveUpdateDestroyAPIView(BaseReservationAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or cancel a specific reservation instance.
    """

    # noinspection PyUnresolvedReferences
    queryset = Reservation.objects.select_related("listing", "user", "listing__user").all()  # type: ignore[attr-defined]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self) -> QuerySet[Reservation]:
        if self.is_swagger_fake_view():
            return Reservation.objects.none()  # type: ignore[attr-defined]
        return (super().get_queryset().filter(
                            Q(user=self.request.user) | Q(listing__user=self.request.user)).distinct())

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.request.method in ["PUT", "PATCH"]:
            return ReservationUpdateSerializer
        return ReservationSerializer


    def delete(self,request: Request,*args: Any,**kwargs: Any,) -> Response:

        reservation: Reservation = self.get_object()
        if reservation.listing.user != request.user:
            return Response(
                        {"detail": "Only the listing owner can delete this reservation."
                                },status=status.HTTP_403_FORBIDDEN,)
        reservation.delete()
        return Response(
            {"detail": "Reservation has been successfully deleted."},status=status.HTTP_200_OK,)


class ReservationCancelAPIView(BaseReservationAPIView, generics.GenericAPIView):
    """
    Action endpoint for quickly cancelling a reservation.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer

    def get_queryset(self) -> QuerySet[Reservation]:
        if self.is_swagger_fake_view():
            return Reservation.objects.none()  # type: ignore[attr-defined]

        # noinspection PyUnresolvedReferences
        return Reservation.objects.select_related("listing", "user", "listing__user")  # type: ignore[attr-defined]

    @extend_schema(summary="Cancel a reservation",request=None,
        responses={
            200: OpenApiResponse(description="Reservation has been successfully cancelled."),
            403: OpenApiResponse(description="You do not have permission to cancel this reservation."),},)


    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        reservation: Reservation = self.get_object()
        if reservation.user != request.user and reservation.listing.user != request.user:
            return Response(
                {"detail": "You do not have permission to cancel this reservation."},status=status.HTTP_403_FORBIDDEN,)

        reservation.status = Reservation.StatusChoice.CANCELLED
        reservation.save(update_fields=["status"])
        return Response({"detail": "Reservation has been successfully cancelled."},status=status.HTTP_200_OK,)