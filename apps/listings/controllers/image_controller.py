"""
API controllers for apartment image endpoints.
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.serializers import BaseSerializer

from apps.listings.controllers.image_schema import (
    image_delete_schema,
    image_upload_schema,
)
from apps.listings.models import Apartment, ApartmentImage
from apps.listings.permissions import IsHostUser
from apps.listings.serializers.images import (
    ApartmentImageSerializer,
    ApartmentImageUploadSerializer,)


@image_upload_schema
class ApartmentImageUploadController(generics.CreateAPIView):
    """Handle apartment image uploads."""

    serializer_class = ApartmentImageUploadSerializer
    permission_classes = [permissions.IsAuthenticated,IsHostUser,]
    parser_classes = [MultiPartParser,FormParser,]

    def perform_create(self,serializer: BaseSerializer,) -> None:
        """Create an image for an apartment owned by the current user."""
        apartment = get_object_or_404(Apartment,pk=self.request.data.get("apartment"),
                            user=self.request.user,)

        serializer.save(apartment=apartment)


@image_delete_schema
class ApartmentImageDeleteController(generics.DestroyAPIView):
    """Handle apartment image deletion."""

    serializer_class = ApartmentImageSerializer
    permission_classes = [permissions.IsAuthenticated,IsHostUser,]

    queryset = ApartmentImage.objects.all()

    def get_object(self) -> ApartmentImage:
        """Return an image owned by the current user."""
        return get_object_or_404(
            ApartmentImage.objects.select_related("apartment"),
                        pk=self.kwargs["pk"],apartment__user=self.request.user,)