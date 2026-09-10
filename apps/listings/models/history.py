"""
Models for tracking search queries and user listing view histories.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedUUIDModel
from apps.listings.models.apartment import Apartment  # 👈 ეს იმპორტი აკლდა!


class SearchHistory(TimeStampedUUIDModel):
    """
    Model tracking search queries executed by users across the platform.
    Enforces non-empty query string rules in clean().
    """

    objects = models.Manager()

    user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE,related_name="search_history",null=True,blank=True,)
    query = models.CharField(max_length=255 )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(query=""),name="search_query_not_empty",),]

    def clean(self) -> None:
        if hasattr(super(), "clean"):
            super().clean()  # type: ignore[misc]

        if self.query is not None:
            self.query = self.query.strip()
            if not self.query:
                raise ValidationError(
                    {"query": "Search query cannot be empty or contain only spaces."})

    def __str__(self) -> str:
        return f"Search: {self.query}"


class ListingViewHistory(TimeStampedUUIDModel):
    """
    Model tracking when users view specific apartment listings.
    Used for recommendations and recent view history.
    """

    objects = models.Manager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="listing_views",null=True,blank=True,)
    listing = models.ForeignKey(Apartment,on_delete=models.CASCADE,related_name="view_history",)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Listing View History"
        verbose_name_plural = "Listing View Histories"

    def clean(self) -> None:
        super().clean()

        if self.listing_id and self.user_id:
            if self.listing.user_id == self.user_id:
                raise ValidationError(
                    {
                        "listing": (
                            "Owners viewing their own listing "
                            "should not generate view history.")})

    def __str__(self) -> str:
        user_identifier = getattr(self.user, "email", "Anonymous")
        listing_title = getattr(self.listing, "title", str(self.listing_id))
        return f"{user_identifier} viewed {listing_title}"