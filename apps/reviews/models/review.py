"""
Review domain model representing listing ratings and feedback.
"""


from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import UUIDAbstractModel
from apps.listings.models import Apartment


class Review(UUIDAbstractModel):
    """
    Model representing a user's review and rating for an apartment listing.
    Enforces domain business rules within clean().
    """

    objects = models.Manager()

    listing = models.ForeignKey(Apartment,on_delete=models.CASCADE,related_name="reviews",)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reviews",)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5),])
    comment = models.TextField(blank=True,null=True,)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True,)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.CheckConstraint(condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                                                    name="review_rating_range_1_to_5",),

            models.UniqueConstraint(fields=["listing", "user"],
                                            name="unique_review_per_user_listing",),]

    def clean(self) -> None:
        super().clean()

        # 1. Rating value validation (1-5 range)

        if self.rating is not None and not (1 <= self.rating <= 5):
            raise ValidationError({"rating": "Rating must be between 1 and 5."})

        # 2. Prevent apartment owners from reviewing their own listings

        listing = getattr(self, "listing", None)
        user_id = getattr(self, "user_id", None)

        if listing and user_id and listing.user_id == user_id:
            raise ValidationError(
                {"listing": "You cannot leave a review for your own listing."})

        # 3. Prevent duplicate reviews by the same user for the same listing

        listing_id = getattr(self, "listing_id", None)
        if listing_id and user_id:
            qs = Review.objects.filter(listing_id=listing_id, user_id=user_id)
            pk = getattr(self, "pk", None)
            if pk:
                qs = qs.exclude(pk=pk)
            if qs.exists():
                raise ValidationError(
                    {"listing": "You have already submitted a review for this listing."})

    def __str__(self) -> str:
        user_identifier: str = getattr(self.user, "username", str(self.user))
        return f"{user_identifier}: {self.rating}"