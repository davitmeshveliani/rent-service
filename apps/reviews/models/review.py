"""
Review domain model representing listing ratings and feedback.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import UUIDAbstractModel
from apps.listings.models import Apartment


class Review(UUIDAbstractModel):
    """
    Model representing a user's review and rating for an apartment listing.
    """

    objects = models.Manager()

    listing = models.ForeignKey(Apartment,on_delete=models.CASCADE,related_name="reviews",)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reviews",)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),
                                                          MaxValueValidator(5),],db_index=True,)
    comment = models.TextField(blank=True,null=True,)
    created_at = models.DateTimeField(
        auto_now_add=True,db_index=True,)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(rating__gte=1),name="review_rating_min_1",),
            models.CheckConstraint(condition=models.Q(rating__lte=5),name="review_rating_max_5",),
            models.UniqueConstraint(fields=["listing", "user"],name="unique_review_per_user_listing",),
              ]

    def __str__(self) -> str:
        user_identifier: str = getattr(self.user, "username", str(self.user))
        return f"{user_identifier}: {self.rating}"