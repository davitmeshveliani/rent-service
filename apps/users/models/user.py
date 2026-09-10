"""
Custom User model definition for the core domain.
Extends Django's AbstractUser with UUID primary key and domain-specific attributes.
"""

import uuid
from typing import ClassVar

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone

from apps.users.choices.choices import GenderChoices


class User(AbstractUser):
    """
    Custom User model extending Django's standard AbstractUser.
    """

    objects = UserManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(unique=True)

    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    birthday = models.DateField(
        blank=True,
        null=True,
    )

    bio = models.TextField(
        blank=True,
        null=True,
    )

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        default=GenderChoices.MALE,
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS: ClassVar[list[str]] = [
        "username",
        "first_name",
        "last_name",
    ]

    class Meta:
        db_table = "users"
        app_label = "users"
        ordering = ["-date_joined"]
        verbose_name = "User"
        verbose_name_plural = "Users"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    gender__in=GenderChoices.values
                ),
                name="user_valid_gender",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(birthday__isnull=True)
                    | models.Q(
                        birthday__lte=timezone.now().date()
                    )
                ),
                name="user_valid_birthday",
            ),
        ]

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

        return self.email
