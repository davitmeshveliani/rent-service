from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.listings.models import Apartment, ListingViewHistory
from apps.listings.serializers.apartments import ApartmentSerializer


class PopularSearchSerializer(serializers.Serializer):
    """
    Read-only serializer for aggregated popular search query endpoints.
    """

    query = serializers.CharField()
    count = serializers.IntegerField()


class ListingViewHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving user's apartment viewing history with nested apartment details.
    """

    apartment = ApartmentSerializer(source="listing",read_only=True)

    class Meta:
        model = ListingViewHistory
        fields = ("id", "apartment", "created_at")
        read_only_fields = ("id", "created_at")


class ListingViewHistoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for recording new apartment views, enforcing model-centric validation.
    """
    apartment = serializers.PrimaryKeyRelatedField(source="listing",queryset=Apartment.objects.all(),)


    class Meta:
        model = ListingViewHistory
        fields = ("id", "apartment")
        read_only_fields = ("id",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        if self.instance:
            instance = ListingViewHistory(
                pk=self.instance.pk,
                user=self.instance.user,
                listing=attrs.get("listing", self.instance.listing),
            )
        else:
            instance = ListingViewHistory(user=user, **attrs)

        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs