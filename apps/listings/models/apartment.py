from djmoney.money import Money

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from djmoney.models.fields import MoneyField

from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError
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

    title = models.CharField(max_length=255,help_text="Title of the apartment listing.",)

    description = models.TextField(blank=True, null=True,
                                         help_text="Detailed description of the apartment.",)

    price = MoneyField(max_digits=10,decimal_places=2,default_currency="EUR",
                                db_index=True,help_text="Rental price of the apartment in EUR.",)


    address_city = models.CharField(max_length=100,db_index=True,
                                         help_text="City where the apartment is located.",)

    address_district = models.CharField(max_length=100,blank=True,
                                    db_index=True,help_text="District where the apartment is located.",)

    rooms = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1),MaxValueValidator(50),],
                                                db_index=True,help_text="Number of rooms in the apartment.",)

    property_type = models.CharField( max_length=50,choices=PropertyTypeChoices.choices,
                                            default=PropertyTypeChoices.APARTMENT,
                                            help_text="Type of the property.",)

    is_active = models.BooleanField(default=True,help_text="Whether the listing is currently active.",)

    views_count = models.PositiveIntegerField(default=0,db_index=True,
                                                help_text="Number of times the listing has been viewed.",)

    average_rating = models.DecimalField(max_digits=3,decimal_places=2,
                                        default=0,help_text="Average rating of the listing from 0.00 to 5.00.",)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                                related_name="apartments",
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

    def clean(self) -> None:
        """
        Custom domain validation logic for Apartment listings.
        """
        super().clean()

        # 1. Title validation
        if self.title and len(self.title.strip()) < 5:
            raise ValidationError(
                {"title": "Title must be at least 5 characters long."})

        # 2. Rooms validation
        if self.rooms and (self.rooms < 1 or self.rooms > 50):
            raise ValidationError(
                {"rooms": "Number of rooms must be between 1 and 50."})

        # 3. Price validation
        if self.price and self.price.amount is not None:
            if self.price.amount <= 0:
                raise ValidationError({"price": "Price must be greater than 0."})

            if self.price.amount > 50000:
                raise ValidationError({"price": "Price cannot exceed 50,000."})

        # 4. Duplicate listing validation
        if self.user_id:
            queryset = Apartment.objects.filter(
                user_id=self.user_id,
                title=self.title,
                address_city=self.address_city,
                address_district=self.address_district,
                rooms=self.rooms,
                property_type=self.property_type,)

            # Exclude the current object during update
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            if queryset.exists():
                raise ValidationError(
                    {"title": "You already have an identical listing."})



    def __str__(self) -> str:
        return f"{self.title} ({self.address_city})"