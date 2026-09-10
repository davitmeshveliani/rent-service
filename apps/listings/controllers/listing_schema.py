from drf_spectacular.utils import (
                                    OpenApiResponse,
                                    extend_schema,
                                    extend_schema_view,
                                    inline_serializer,)
from rest_framework import serializers

from apps.listings.serializers import (
                                        ApartmentCreateUpdateSerializer,
                                        ApartmentSerializer,)

ErrorSchema = inline_serializer(
    name="ListingControllerErrorResponse",
    fields={"detail": serializers.CharField(default="Error detail message.")},)

request_media_types = {
                        "application/json": ApartmentCreateUpdateSerializer,
                        "multipart/form-data": ApartmentCreateUpdateSerializer,
                        "application/x-www-form-urlencoded": ApartmentCreateUpdateSerializer,}

listing_list_create_schema = extend_schema_view(
    get=extend_schema(
        summary="List active apartments",
        description=(
                    "Public endpoint for active apartment listings "
                    "with filtering, search, and ordering."),
        operation_id="listings_list",
        auth=[],
        responses={200: ApartmentSerializer(many=True)},),
    post=extend_schema(
        summary="Create a new apartment listing",
        description="Authenticated hosts can create new property listings.",
        operation_id="listings_create",
        request=request_media_types,
        responses={
                    201: ApartmentSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    403: OpenApiResponse(response=ErrorSchema, description="Host access required"),},),)

my_listings_schema = extend_schema(
    summary="List host's own listings",
    description="Retrieves all listings owned by the authenticated host.",
    responses={
                200: ApartmentSerializer(many=True),
                401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                403: OpenApiResponse(response=ErrorSchema, description="Host access required"),},)

listing_detail_schema = extend_schema_view(
    get=extend_schema(
        summary="Retrieve an apartment",
        description=(
                    "Retrieves an apartment listing. Public users "
                    "can access active listings. Owners can also "
                    "access their inactive listings."),
        operation_id="listings_retrieve",
        responses={
            200: ApartmentSerializer,
            404: OpenApiResponse(response=ErrorSchema, description="Apartment not found"),},),
    put=extend_schema(
        summary="Update an apartment",
        operation_id="listings_update",
        request=request_media_types,
        responses={
                    200: ApartmentSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    403: OpenApiResponse(response=ErrorSchema, description="Owner access required"),
                    404: OpenApiResponse(response=ErrorSchema, description="Apartment not found"),},),
    patch=extend_schema(
        summary="Partially update an apartment",
        operation_id="listings_partial_update",
        request=request_media_types,
        responses={
                    200: ApartmentSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    403: OpenApiResponse(response=ErrorSchema, description="Owner access required"),
                    404: OpenApiResponse(response=ErrorSchema, description="Apartment not found"),},),
    delete=extend_schema(
        summary="Delete an apartment",
        operation_id="listings_delete",
        responses={
                    204: OpenApiResponse(description="Listing deleted successfully"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    403: OpenApiResponse(response=ErrorSchema, description="Owner access required"),
                    404: OpenApiResponse(response=ErrorSchema, description="Apartment not found"),},),)