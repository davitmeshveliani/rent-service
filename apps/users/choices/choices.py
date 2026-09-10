"""
Choice enumerations for the Users application domain.
Provides structured options for user gender.
"""

from django.db import models


__all__: list[str] = [
    "GenderChoices",
]


class GenderChoices(models.TextChoices):
    """
    Enumeration for user gender options.
    """

    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"

