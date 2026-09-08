from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from djmoney.models.fields import MoneyField

from simple_history.models import HistoricalRecords

from apps.core.managers import ListingManager
from apps.core.models import TimeStampedUUIDModel


class PropertyTypeChoices(models.TextChoices):
    """
    Enumeration for supported apartment property types.
    """

    APARTMENT = "apartment", "Apartment"
    HOUSE = "house", "House"
    STUDIO = "studio", "Studio"
    VILLA = "villa", "Villa"


class Apartment(TimeStampedUUIDModel):
    """
    Core domain model representing a real estate listing.
    """

    objects = ListingManager()
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    price = MoneyField(
                        max_digits=10,
                        decimal_places=2,
                        default_currency="EUR",
                        validators=[MinValueValidator(Decimal("0.01"))],db_index=True,)
    address_city = models.CharField(max_length=100, db_index=True,)
    address_district = models.CharField(max_length=100,blank=True,db_index=True,)
    rooms = models.PositiveIntegerField(
                                default=1,
                                validators=[MinValueValidator(1),MaxValueValidator(50),],db_index=True,)
    property_type = models.CharField(
                                max_length=50,
                                choices=PropertyTypeChoices.choices,
                                default=PropertyTypeChoices.APARTMENT,
                                db_index=True,)

    is_active = models.BooleanField(default=True,db_index=True,)
    views_count = models.PositiveIntegerField(default=0,db_index=True,)
    user = models.ForeignKey(
                                settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name="apartments",
                                db_index=True,)

    history = HistoricalRecords()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                                    condition=models.Q(price__gt=0),
                                    name="apartment_price_positive",),
            models.CheckConstraint(
                                    condition=models.Q(rooms__gte=1),
                                    name="apartment_rooms_min_1",),
            models.CheckConstraint(
                                condition=models.Q(rooms__lte=50),
                                name="apartment_rooms_max_50",),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.address_city})"