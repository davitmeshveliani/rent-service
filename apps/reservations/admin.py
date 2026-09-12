from django.contrib import admin
from apps.reservations.models import Reservation
from simple_history.admin import SimpleHistoryAdmin


@admin.register(Reservation)
class ReservationAdmin(SimpleHistoryAdmin):
    list_select_related = ("listing", "user")

    list_display = ("id", "listing", "user", "status", "start_date", "end_date", "created_at")
    list_filter = ("status", "start_date", "end_date", "created_at")
    search_fields = ("listing__title", "user__username", "user__email")

    ordering = ("-created_at",)
    readonly_fields = ("created_at",)