from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedUUIDModel
from apps.listings.models.apartment import Apartment


class SearchHistory(TimeStampedUUIDModel):
    """
    Model tracking search queries executed by users across the platform.
    """
    objects = models.Manager()
    user = models.ForeignKey(
                            settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                            related_name="search_history",null=True,blank=True,)
    query = models.CharField(max_length=255, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                                    condition=~models.Q(query=""),
                                    name="search_query_not_empty",),]

    def __str__(self) -> str:
        return f"Search: {self.query}"


class ListingViewHistory(TimeStampedUUIDModel):
    """
    Model for recording viewing history of apartments by authenticated/anonymous users.
    """
    objects = models.Manager()
    user = models.ForeignKey(
                            settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                            related_name="view_history",null=True,blank=True,)
    apartment = models.ForeignKey(Apartment,on_delete=models.CASCADE,related_name="views_history",)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"View: Apartment {self.apartment_id}"