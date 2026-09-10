from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedUUIDModel
from apps.listings.models.apartment import Apartment


class ApartmentImage(TimeStampedUUIDModel):
    """
    Model representing photo attachments linked to a specific apartment listing.
    """

    objects = models.Manager()

    apartment = models.ForeignKey(Apartment,on_delete=models.CASCADE,related_name="images")
    image = models.ImageField(upload_to="apartment_images/")
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def clean(self) -> None:
        super().clean()

        if self.is_main and self.apartment_id:
            qs = ApartmentImage.objects.filter(apartment_id=self.apartment_id,is_main=True,)

            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError(
                    {"is_main": (
                            "This apartment already has a main image.")})
    def __str__(self) -> str:
        return f"Image for {self.apartment.title if hasattr(self, 'apartment') else self.apartment_id}"