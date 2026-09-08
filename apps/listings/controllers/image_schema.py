"""
OpenAPI schema definitions for apartment image endpoints.
"""

from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.listings.serializers.images import (ApartmentImageSerializer,
                                              ApartmentImageUploadSerializer,)

image_upload_schema = extend_schema(
    summary="Upload an apartment image",
    description=("Allows an authenticated host to upload an image "
                            "for an apartment they own."),
    request={"multipart/form-data": ApartmentImageUploadSerializer,},
    responses={
                201: ApartmentImageSerializer,
                400: OpenApiResponse(description="Validation Error",),
                401: OpenApiResponse(description="Authentication required",),
                403: OpenApiResponse(description="Host access required",),},)



image_delete_schema = extend_schema(
    summary="Delete an apartment image",
    description=(
                    "Allows an authenticated host to delete an image "
                    "belonging to an apartment they own."),
    responses={
                204: OpenApiResponse(
                    description="Image deleted successfully",),
                401: OpenApiResponse(
                    description="Authentication required",),
                403: OpenApiResponse(
                    description="Host access required", ),
                404: OpenApiResponse(description="Image not found",
                            ),},)