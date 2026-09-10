from drf_spectacular.utils import (
                                    OpenApiResponse,
                                    extend_schema,
                                    extend_schema_view,
                                    inline_serializer,)
from rest_framework import serializers

from apps.reviews.serializers import ReviewSerializer

ErrorSchema = inline_serializer(
                                name="ReviewControllerErrorResponse",
                                fields={"detail": serializers.CharField(default="Error detail message.")},)

# Request body-ს
review_request_types = {
                        "application/json": ReviewSerializer,
                        "multipart/form-data": ReviewSerializer,
                        "application/x-www-form-urlencoded": ReviewSerializer,}

# 1. List & Create Schema
review_list_create_schema = extend_schema_view(
    get=extend_schema(
        summary="List or filter reviews",
        description="Public endpoint to list reviews. Can be filtered by rating or listing ID.",
        operation_id="reviews_list",
        auth=[],
        responses={
                    200: ReviewSerializer(many=True),},),
    post=extend_schema(
        summary="Create a new review",
        description="Requires authentication. User is automatically set from token.",
        operation_id="reviews_create",
        request=review_request_types,
        responses={
                    201: ReviewSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),},),)

# 2. My Reviews Schema
my_reviews_schema = extend_schema(
    summary="Get authenticated user's reviews",
    description="Retrieve all reviews created by the currently logged-in user.",
    operation_id="reviews_my_list",
    responses={
                200: ReviewSerializer(many=True),
                401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),},)

# 3. Detail, Update & Delete Schema
review_detail_schema = extend_schema_view(
    get=extend_schema(
        summary="Retrieve review details",
        operation_id="reviews_retrieve",
        auth=[],
        responses={
                    200: ReviewSerializer,
                    404: OpenApiResponse(response=ErrorSchema, description="Review not found"),},),
    put=extend_schema(
        summary="Update a review",
        operation_id="reviews_update",
        request=review_request_types,
        responses={
                    200: ReviewSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    403: OpenApiResponse(response=ErrorSchema, description="Permission denied"),
                    404: OpenApiResponse(response=ErrorSchema, description="Review not found"),},),
    patch=extend_schema(
        summary="Partially update a review",
        operation_id="reviews_partial_update",
        request=review_request_types,
        responses={
                    200: ReviewSerializer,
                    400: OpenApiResponse(response=ErrorSchema, description="Validation Error"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    403: OpenApiResponse(response=ErrorSchema, description="Permission denied"),
                    404: OpenApiResponse(response=ErrorSchema, description="Review not found"),},),
    delete=extend_schema(
        summary="Delete a review",
        operation_id="reviews_delete",
        responses={
                    204: OpenApiResponse(description="Review deleted successfully"),
                    401: OpenApiResponse(response=ErrorSchema, description="Unauthorized"),
                    403: OpenApiResponse(response=ErrorSchema, description="Permission denied"),
                    404: OpenApiResponse(response=ErrorSchema, description="Review not found"),},),)