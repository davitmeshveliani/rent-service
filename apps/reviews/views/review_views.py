"""
Views for listing reviews and ratings.
"""

from decimal import Decimal

from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema_view

from apps.listings.models import Apartment
from apps.listings.permissions import IsOwnerOrReadOnly
from apps.reviews.models import Review
from apps.reviews.schemas.review_schema import (
                                                    my_reviews_schema,
                                                    review_detail_schema,
                                                    review_list_create_schema,
                                                )
from apps.reviews.serializers import ReviewSerializer


def update_average_rating(listing_id):
    """
    Recalculate and store the average rating for a listing.
    """
    average = (Review.objects.filter(listing_id=listing_id)
                            .aggregate(average=Avg("rating"))["average"])

    if average is None:
        average = Decimal("0.00")

    Apartment.objects.filter(pk=listing_id).update(average_rating=average)


@review_list_create_schema
class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rating", "listing"]

    def get_queryset(self):
        return Review.objects.select_related("listing","user","listing__user",).all()

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        update_average_rating(review.listing_id)


@extend_schema_view(get=my_reviews_schema)
class MyReviewsAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Review.objects.none()

        return (Review.objects.filter(user=self.request.user)
                        .select_related("listing","user","listing__user",)
                        .order_by("-created_at"))


@review_detail_schema
class ReviewRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                                    IsOwnerOrReadOnly,
                                ]
    lookup_field = "pk"

    def get_queryset(self):
        return Review.objects.select_related("listing","user","listing__user",).all()

    def perform_update(self, serializer):
        old_listing_id = serializer.instance.listing_id

        review = serializer.save()
        new_listing_id = review.listing_id

        update_average_rating(old_listing_id)

        if new_listing_id != old_listing_id:
            update_average_rating(new_listing_id)

    def perform_destroy(self, instance):
        listing_id = instance.listing_id
        instance.delete()
        update_average_rating(listing_id)