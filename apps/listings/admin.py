"""
Django Admin panel configurations for the Listings domain models.
Includes query optimizations (list_select_related) to prevent N+1 issues in the admin interface.
"""

from typing import ClassVar

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from apps.listings.models import (
    Apartment,
    ApartmentImage,
    ListingViewHistory,
    SearchHistory,
)


class ApartmentImageInline(admin.TabularInline):
    """
    Inline admin configuration for managing apartment images directly within the Apartment form.
    """

    model = ApartmentImage
    extra = 1


@admin.register(Apartment)
class ApartmentAdmin(SimpleHistoryAdmin):
    """
    Admin configuration for managing Apartment listings.
    """

    list_select_related = ("user",)
    list_display = ("title","address_city",
                                    "price","rooms","property_type",
                                    "is_active","views_count","user","created_at",)

    list_filter = ("is_active", "property_type", "address_city", "created_at")
    search_fields = ("title","description","address_city","user__username","user__email",)
    ordering = ("-created_at",)
    readonly_fields = ("views_count", "created_at")
    inlines: ClassVar[list[type[admin.TabularInline]]] = [ApartmentImageInline]


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for viewing user search query history.
    """

    list_select_related = ("user",)
    list_display = ("query", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("query", "user__username", "user__email")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(ListingViewHistory)
class ListingViewHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for tracking apartment viewing history.
    """

    list_select_related = ("listing", "user")
    list_display = ("listing", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("listing__title", "user__username", "user__email")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)