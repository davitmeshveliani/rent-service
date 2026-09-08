"""
API controllers for apartment listing endpoints.
"""

from typing import Any

from django.db.models import F, QuerySet
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.listings.controllers.listing_schema import (
                                                        listing_detail_schema,
                                                        listing_list_create_schema,
                                                        my_listings_schema,
                                                            )
from apps.listings.filters import ApartmentFilter
from apps.listings.models import Apartment, ListingViewHistory
from apps.listings.permissions import IsHostUser, IsOwnerOrReadOnly
from apps.listings.serializers import (
                                ApartmentCreateUpdateSerializer,
                                ApartmentSerializer,)
from apps.listings.services.listing_service import ListingService
from apps.users.authentication import CookieJWTAuthentication


@listing_list_create_schema
class ListingListCreateController(generics.ListCreateAPIView):
    """Handle listing creation and public listing retrieval."""

    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter,]
    filterset_class = ApartmentFilter
    search_fields = ["title","description","address_city","address_district",]
    ordering_fields = ["price","created_at","rooms","views_count",]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = ListingService()

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Return the serializer according to the request method."""
        if self.request.method == "POST":
            return ApartmentCreateUpdateSerializer

        return ApartmentSerializer

    def get_permissions(self,) -> list[permissions.BasePermission]:
        """Apply permissions according to the request method."""
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(),IsHostUser(),]
        return [permissions.AllowAny()]

    def get_queryset(self) -> QuerySet[Apartment]:
        """Return active apartment listings."""
        if getattr(self,"swagger_fake_view",False,):
            return Apartment.objects.none()
        return self.service.get_active_listings()

    def perform_create(self,serializer: BaseSerializer,) -> None:
        """Assign the authenticated user as the listing owner."""
        serializer.save(user=self.request.user)


@my_listings_schema
class MyListingsController(generics.ListAPIView):
    """Handle retrieval of the authenticated host's listings."""

    serializer_class = ApartmentSerializer
    permission_classes = [permissions.IsAuthenticated,IsHostUser,]
    filter_backends = [DjangoFilterBackend,]
    filterset_class = ApartmentFilter

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = ListingService()

    def get_queryset(self) -> QuerySet[Apartment]:
        """Return listings owned by the authenticated user."""
        if getattr(self,"swagger_fake_view",False,):
            return Apartment.objects.none()

        return self.service.get_user_listings(
            self.request.user)


@listing_detail_schema
class ListingDetailController(generics.RetrieveUpdateDestroyAPIView):
    """Handle retrieving, updating, and deleting a listing."""

    authentication_classes = (CookieJWTAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly,]
    lookup_field = "pk"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = ListingService()

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Return the serializer according to the request method."""
        if self.request.method in ["PUT","PATCH",]:
            return ApartmentCreateUpdateSerializer
        return ApartmentSerializer

    def get_object(self) -> Apartment:
        """Retrieve the listing and validate object permissions."""
        listing_id = self.kwargs[self.lookup_field]

        listing = self.service.get_listing(
            listing_id=listing_id,
            user=(self.request.user
                            if self.request.user.is_authenticated else None),)

        if listing is None:
            raise Http404("Apartment not found.")
        self.check_object_permissions(self.request,listing,)

        return listing

    def retrieve(self,request: Request,*args: Any,**kwargs: Any,) -> Response:
        """Return the listing and update its view statistics."""
        listing = self.get_object()
        ListingViewHistory.objects.create(
            user=(request.user if request.user.is_authenticated else None),
                        apartment=listing,)

        Apartment.objects.filter(
            pk=listing.pk).update(views_count=F("views_count") + 1)

        listing.refresh_from_db(fields=["views_count"])
        serializer = self.get_serializer(listing)
        return Response(serializer.data)



    def destroy(self,request: Request,*args: Any,**kwargs: Any,) -> Response:
        """Soft-delete the listing by deactivating it."""
        listing = self.get_object()
        self.service.deactivate_listing(listing=listing,user=request.user,)

        return Response(status=204)