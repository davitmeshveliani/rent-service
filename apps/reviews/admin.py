from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Review


@admin.register(Review)
class ReviewAdmin(SimpleHistoryAdmin):
    list_select_related = ("listing", "user")
    list_display = ("id", "listing", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("listing__title", "comment")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)