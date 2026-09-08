"""
Repository layer for apartment listing database queries.
"""

from typing import Any

from django.db.models import Count, QuerySet

from apps.listings.models import Apartment


class ListingRepository:
    """
    Handles database queries related to apartment listings.
    """

    def get_active_listings(self) -> QuerySet[Apartment]:
        return (
                Apartment.objects
                .filter(is_active=True)
                .select_related("user")
                .prefetch_related("images")
                .order_by("-created_at")
        )

    def get_user_listings(self, user: Any) -> QuerySet[Apartment]:
        return (
            Apartment.objects
            .filter(user=user)
            .select_related("user")
            .prefetch_related("images")
            .order_by("-created_at")
                )

    def get_listing_by_id(self, listing_id: Any) -> Apartment:
        return (
                    Apartment.objects
                    .select_related("user")
                    .prefetch_related("images")
                    .get(pk=listing_id)
                )

    def get_popular_listings(self) -> QuerySet[Apartment]:
        return (
                    Apartment.objects
                    .filter(is_active=True)
                    .select_related("user")
                    .prefetch_related("images")
                    .annotate(reviews_count=Count("reviews",distinct=True,))
                    .order_by("-views_count","-reviews_count","-created_at",)
                )