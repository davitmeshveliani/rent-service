"""
Application configuration for the Listings domain.
"""

from django.apps import AppConfig


class ListingsConfig(AppConfig):
    """
    AppConfig for managing listings application setup and settings.
    """

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "apps.listings"