from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.listings.models import ApartmentImage


class ApartmentImageSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving attached apartment images.
    """

    class Meta:
        model = ApartmentImage
        fields = ("id", "image", "is_main", "created_at")
        read_only_fields = ("id", "created_at")


class ApartmentImageUploadSerializer(serializers.ModelSerializer):
    """
    Serializer used for uploading apartment images.
    Delegates validation (e.g. main image uniqueness) to Model.clean().
    """

    image = serializers.ImageField(required=True)

    class Meta:
        model = ApartmentImage
        fields = ("id", "apartment", "image", "is_main")
        read_only_fields = ("id",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Executes instance.full_clean() to leverage Model.clean() logic.
        """
        if self.instance:
            instance = ApartmentImage(
                pk=self.instance.pk,
                apartment=self.instance.apartment,
                image=attrs.get("image", self.instance.image),
                is_main=attrs.get("is_main", self.instance.is_main),
            )
        else:
            instance = ApartmentImage(**attrs)

        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs