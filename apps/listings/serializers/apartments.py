from decimal import Decimal
from moneyed import Money
from rest_framework import serializers

from apps.listings.models import Apartment
from apps.listings.serializers.images import ApartmentImageSerializer


class ApartmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = (
            "title",
            "description",
            "price",
            "address_city",
            "address_district",
            "rooms",
            "property_type",
            "is_active",
        )

    def validate_price(self, value: Money) -> Money:
        if value.amount <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )

        if value.amount > 50000:
            raise serializers.ValidationError(
                "Price cannot exceed 50,000."
            )

        return value

    def validate_rooms(self, value: int) -> int:
        if value < 1:
            raise serializers.ValidationError(
                "Apartment must have at least 1 room."
            )

        if value > 50:
            raise serializers.ValidationError(
                "Number of rooms must be realistic."
            )

        return value

    def validate_title(self, value: str) -> str:
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long."
            )

        return value.strip()

    def validate(self, attrs):
        user = self.context["request"].user

        duplicate_exists = Apartment.objects.filter(
            user=user,
            title=attrs.get("title"),
            address_city=attrs.get("address_city"),
            address_district=attrs.get("address_district", ""),
            rooms=attrs.get("rooms"),
            property_type=attrs.get("property_type"),
        ).exists()

        if duplicate_exists:
            raise serializers.ValidationError(
                "You already have an identical listing."
            )

        return attrs


class ApartmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True,help_text="User who owns the listing.",)
    images = ApartmentImageSerializer(many=True, read_only=True,help_text="List of attached apartment images.",)

    average_rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        read_only=True,
        help_text="Average rating of the listing from 0.00 to 5.00.",
    )

    class Meta:
        model = Apartment
        fields = (
            "id",
            "title",
            "description",
            "price",
            "address_city",
            "address_district",
            "rooms",
            "property_type",
            "is_active",
            "views_count",
            "average_rating",
            "user",
            "images",
            "created_at",
        )

        read_only_fields = (
            "id",
            "user",
            "views_count",
            "average_rating",
            "created_at",
        )