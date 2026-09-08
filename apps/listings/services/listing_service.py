"""
Service layer for apartment listing business logic.
"""

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from apps.listings.models import Apartment
from apps.listings.repositories.listing_repository import (ListingRepository,)


class ListingService:
    """
    Handles business logic for apartment listings.
    """

    def __init__(self) -> None:
        self.repository = ListingRepository()

    def get_active_listings(self) -> QuerySet[Apartment]:
        return self.repository.get_active_listings()

    def get_user_listings(self,user: Any,) -> QuerySet[Apartment]:
        return self.repository.get_user_listings(user)

    def get_popular_listings(self) -> QuerySet[Apartment]:
        return self.repository.get_popular_listings()

    def get_listing(self,listing_id: Any,user: Any = None,) -> Apartment | None:
        try:
            listing = self.repository.get_listing_by_id(listing_id)
        except ObjectDoesNotExist:
            return None
        if listing.is_active:
            return listing
        if user and listing.user == user:
            return listing
        return None


    def can_manage_listing(self,listing: Apartment,user: Any,) -> bool:
        return listing.user == user


    def activate_listing(self,listing: Apartment,user: Any,) -> bool:
        if not self.can_manage_listing(listing, user):
            return False
        if listing.is_active:
            return True

        listing.is_active = True
        listing.save(update_fields=["is_active"])
        return True

    def deactivate_listing(self,listing: Apartment,user: Any,) -> bool:
        if not self.can_manage_listing(listing, user):
            return False
        if not listing.is_active:
            return True
        listing.is_active = False
        listing.save(update_fields=["is_active"])
        return True