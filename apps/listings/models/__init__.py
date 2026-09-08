"""
Models package for the Listings application domain.
"""

from apps.listings.models.apartment import Apartment, PropertyTypeChoices
from apps.listings.models.apartment_image import ApartmentImage
from apps.listings.models.history import ListingViewHistory, SearchHistory

__all__: list[str] = ["Apartment","ApartmentImage",
                        "PropertyTypeChoices","SearchHistory","ListingViewHistory",]