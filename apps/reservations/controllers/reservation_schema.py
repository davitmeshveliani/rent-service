from drf_spectacular.utils import (
                                    OpenApiResponse,
                                    extend_schema,
                                    extend_schema_view,
                                    inline_serializer,)
from rest_framework import serializers

from apps.reservations.serializers import (
                                            ReservationSerializer,
                                            ReservationUpdateSerializer,)

ErrorSchema = inline_serializer(
                        name="ReservationControllerErrorResponse",
                        fields={"detail": serializers.CharField(default="Error detail message.")},)

# Request body-ს
reservation_create_request_types = {
                                    "application/json": ReservationSerializer,
                                    "multipart/form-data": ReservationSerializer,
                                    "application/x-www-form-urlencoded": ReservationSerializer,}

reservation_update_request_types = {
                                "application/json": ReservationUpdateSerializer,
                                "multipart/form-data": ReservationUpdateSerializer,
                                "application/x-www-form-urlencoded": ReservationUpdateSerializer,}

# 1. List & Create Schema
reservation_list_create_schema = extend_schema_view(
    get=extend_schema(
        summary="List user-related reservations",
        description="Retrieves all reservations where the authenticated user is either the guest or the host.",
        operation_id="reservations_list",
        responses={
                    200: ReservationSerializer(many=True),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),},),
    post=extend_schema(
        summary="Create a new reservation",
        description="Guest creates a booking request for a listing.",
        operation_id="reservations_create",
        request=reservation_create_request_types,
        responses={
                    201: ReservationSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),},),)

# 2. My Reservations Schema
my_reservations_schema = extend_schema(
    summary="List guest's own reservations",
    description="Retrieves all reservations booked by the authenticated guest user.",
    operation_id="reservations_my_list",
    responses={
                200: ReservationSerializer(many=True),
                401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),},)

# 3. Host Reservations Schema
host_reservations_schema = extend_schema(
    summary="List host's incoming reservation requests",
    description="Retrieves all booking requests for listings owned by the authenticated host.",
    operation_id="reservations_host_list",
    responses={
                200: ReservationSerializer(many=True),
                401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),},)

# 4. Detail, Update & Delete Schema
reservation_detail_schema = extend_schema_view(
    get=extend_schema(
        summary="Retrieve a reservation",
        operation_id="reservations_retrieve",
        responses={
                    200: ReservationSerializer,
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    404: OpenApiResponse(response=ErrorSchema, description="Reservation not found"),},),
    put=extend_schema(
        summary="Update a reservation",
        operation_id="reservations_update",
        request=reservation_update_request_types,
        responses={
                    200: ReservationSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    404: OpenApiResponse(response=ErrorSchema, description="Reservation not found"),},),
    patch=extend_schema(
        summary="Partially update a reservation",
        operation_id="reservations_partial_update",
        request=reservation_update_request_types,
        responses={
                    200: ReservationSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    404: OpenApiResponse(response=ErrorSchema, description="Reservation not found"),},),
    delete=extend_schema(
        summary="Delete a reservation",
        operation_id="reservations_delete",
        responses={
                    200: OpenApiResponse(description="Reservation has been successfully deleted."),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    403: OpenApiResponse(response=ErrorSchema, description="Only owner can delete"),
                    404: OpenApiResponse(response=ErrorSchema, description="Reservation not found"),},),)

# 5. Cancel Reservation Schema
reservation_cancel_schema = extend_schema(
    summary="Cancel a reservation",
    operation_id="reservations_cancel",
    request=None,
    responses={
                200: OpenApiResponse(description="Reservation has been successfully cancelled."),
                401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                403: OpenApiResponse(response=ErrorSchema, description="No permission to cancel"),
                404: OpenApiResponse(response=ErrorSchema, description="Reservation not found"),},)