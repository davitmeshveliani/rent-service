from decimal import Decimal
from moneyed import Money
from rest_framework import serializers

from apps.listings.models import Apartment
from apps.listings.serializers.images import ApartmentImageSerializer


class ApartmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ("title","description","price","address_city",
                  "address_district","rooms","property_type","is_active",)

    def validate_price(self, value: Money) -> Money:
        if value.amount <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        if value.amount > 50000:
            raise serializers.ValidationError("Price cannot exceed 50,000.")
        return value


    def validate_rooms(self, value: int) -> int:
        if value < 1:
            raise serializers.ValidationError("Apartment must have at least 1 room.")


        if value > 50:
            raise serializers.ValidationError("Number of rooms must be realistic.")
        return value


    def validate_title(self, value: str) -> str:
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value.strip()


class ApartmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    images = ApartmentImageSerializer(many=True,read_only=True,)


    class Meta:
        model = Apartment
        fields = ("id","title","description","price","address_city","address_district",
                   "rooms","property_type","is_active","views_count","user","images","created_at",)

        read_only_fields = ("id","user","views_count","created_at",)