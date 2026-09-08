from rest_framework import serializers
from apps.listings.models import ApartmentImage


class ApartmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentImage
        fields = ("id", "image", "is_main", "created_at")
        read_only_fields = ("id", "created_at")


class ApartmentImageUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = ApartmentImage
        fields = ("id", "apartment", "image", "is_main")
        read_only_fields = ("id",)