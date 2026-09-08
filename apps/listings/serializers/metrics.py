from rest_framework import serializers
from apps.listings.models import ListingViewHistory
from apps.listings.serializers.apartments import ApartmentSerializer


class PopularSearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    count = serializers.IntegerField()


class ListingViewHistorySerializer(serializers.ModelSerializer):
    apartment = ApartmentSerializer(read_only=True)

    class Meta:
        model = ListingViewHistory
        fields = ("id", "apartment", "created_at")