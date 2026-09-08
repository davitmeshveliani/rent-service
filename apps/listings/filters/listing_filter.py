"""
Filter sets for querying and narrowing down apartment listings.
"""

from typing import ClassVar

import django_filters

from apps.listings.models import Apartment


class ApartmentFilter(django_filters.FilterSet):
    """
    Custom filter set for the Apartment model allowing price range,
    room counts, city, district, and property type filtering.
    """

    min_price = django_filters.NumberFilter(
                                    field_name="price",
                                    lookup_expr="gte",)

    max_price = django_filters.NumberFilter(
                                    field_name="price",
                                    lookup_expr="lte",)

    min_rooms = django_filters.NumberFilter(
                                    field_name="rooms",
                                    lookup_expr="gte",)

    max_rooms = django_filters.NumberFilter(
                                    field_name="rooms",
                                    lookup_expr="lte",)

    city = django_filters.CharFilter(
                                    field_name="address_city",
                                    lookup_expr="iexact",)

    district = django_filters.CharFilter(
                            field_name="address_district",
                            lookup_expr="iexact",)

    property_type = django_filters.CharFilter(
                            field_name="property_type",
                            lookup_expr="iexact",)

    class Meta:
        model = Apartment
        fields: ClassVar[list[str]] = [
                                        "min_price","max_price","min_rooms","max_rooms",
                                        "city","district","property_type",
                                        ]