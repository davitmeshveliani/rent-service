"""
Compatibility exports for listing controllers.

The actual API logic lives in:
apps.listings.controllers.listing_controller
"""

from apps.listings.controllers.listing_controller import (
    ListingDetailController,
    ListingListCreateController,
    MyListingsController,
)

ListingListCreateAPIView = ListingListCreateController
MyListingsAPIView = MyListingsController
ListingRetrieveUpdateDestroyAPIView = ListingDetailController

__all__ = [
    "ListingListCreateAPIView",
    "MyListingsAPIView",
    "ListingRetrieveUpdateDestroyAPIView",
]