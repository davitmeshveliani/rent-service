"""
Choice enumerations for the Users application domain.
Provides structured options for user gender and system roles.
"""

from django.db import models

__all__: list[str] = [
                "GenderChoices",
                "RoleChoices",]


class GenderChoices(models.TextChoices):
    """
    Enumeration for user gender options.
    """

    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"


class RoleChoices(models.TextChoices):
    """
    Enumeration for user system role types.
    """

    HOST = "HOST", "Host"
    GUEST = "GUEST", "Guest"
    BOTH = "BOTH", "Both"