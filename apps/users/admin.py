"""
Admin configuration for custom User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email","username","is_active","is_staff",)
    list_filter = ("is_active","is_staff",)
    search_fields = ("email","username",)