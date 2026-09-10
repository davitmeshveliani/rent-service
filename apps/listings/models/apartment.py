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

    title = models.CharField(
                                max_length=255,
                                db_index=True,
                                help_text="Title of the apartment listing.",)

    description = models.TextField(
                                    blank=True,
                                    null=True,
                                    help_text="Detailed description of the apartment.",)

    price = MoneyField(
                        max_digits=10,
                        decimal_places=2,
                        default_currency="EUR",
                        validators=[MinValueValidator(Decimal("0.01")),],
                        db_index=True,
                        help_text="Rental price of the apartment in EUR.",)

    address_city = models.CharField(
                                    max_length=100,
                                    db_index=True,
                                    help_text="City where the apartment is located.",)

    address_district = models.CharField(
                            max_length=100,
                            blank=True,
                            db_index=True,
                            help_text="District where the apartment is located.",)

    rooms = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1),MaxValueValidator(50),],
        db_index=True,
        help_text="Number of rooms in the apartment.",)

    property_type = models.CharField(
                                    max_length=50,
                                    choices=PropertyTypeChoices.choices,
                                    default=PropertyTypeChoices.APARTMENT,
                                    db_index=True,
                                    help_text="Type of the property.",)

    is_active = models.BooleanField(
                                    default=True,
                                    db_index=True,
                                    help_text="Whether the listing is currently active.",)

    views_count = models.PositiveIntegerField(
                                                default=0,
                                                db_index=True,
                                                help_text="Number of times the listing has been viewed.",)

    average_rating = models.DecimalField(
                                        max_digits=3,
                                        decimal_places=2,
                                        default=0,
                                        db_index=True,
                                        help_text="Average rating of the listing from 0.00 to 5.00.",)

    user = models.ForeignKey(
                            settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE,
                            related_name="apartments",
                            db_index=True,
                            help_text="User who owns the listing.",)

    history = HistoricalRecords()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
                        models.CheckConstraint(condition=models.Q(price__gt=0),
                                                        name="apartment_price_positive",),
                        models.CheckConstraint(condition=models.Q(rooms__gte=1),
                                                            name="apartment_rooms_min_1",),
                        models.CheckConstraint(condition=models.Q(rooms__lte=50),
                                                            name="apartment_rooms_max_50",),
            models.UniqueConstraint(
                fields=["user","title","address_city","address_district","rooms","property_type",],
                name="unique_apartment_listing",),]

    def __str__(self) -> str:
        return f"{self.title} ({self.address_city})"