from django.db import models

from apps.core.models import TimeStampedUUIDModel
from apps.listings.models.apartment import Apartment


class ApartmentImage(TimeStampedUUIDModel):
    """
    Model representing photo attachments linked to a specific apartment listing.
    """
    objects = models.Manager()
    apartment = models.ForeignKey(Apartment,on_delete=models.CASCADE,related_name="images",db_index=True,)
    image = models.ImageField(upload_to="apartment_images/")
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Image for {self.apartment.title}"
