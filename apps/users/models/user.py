"""
Custom User model definition for the core domain.
Extends Django's AbstractUser with UUID primary key and domain-specific attributes.
"""

import uuid


from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.users.choices.choices import GenderChoices


class User(AbstractUser):
    """
    Custom User model extending Django's standard AbstractUser.
    """

    objects = UserManager()

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150,blank=True,null=True,)
    last_name = models.CharField(max_length=150,blank=True,null=True,)
    phone_number = models.CharField(max_length=20,blank=True,null=True,)
    address = models.CharField(max_length=255,blank=True,null=True,)
    birthday = models.DateField(blank=True,null=True,)
    bio = models.TextField(blank=True,null=True,)

    gender = models.CharField(max_length=10,choices=GenderChoices.choices,default=GenderChoices.MALE,)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username","first_name","last_name",]

    class Meta:
        db_table = "users"
        app_label = "users"
        ordering = ["-date_joined"]
        verbose_name = "User"
        verbose_name_plural = "Users"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    gender__in=GenderChoices.values),
                name="user_valid_gender",),
            models.CheckConstraint(
                condition=(
                    models.Q(birthday__isnull=True) | models.Q(birthday__lte=timezone.now().date())),
                                                    name="user_valid_birthday",)]

    def clean(self) -> None:
        super().clean()

        # 1. Email normalization & case-insensitive uniqueness check
        if self.email:
            self.email = self.email.strip().lower()
            qs = User.objects.filter(email__iexact=self.email)
            pk = getattr(self, "pk", None)
            if pk:
                qs = qs.exclude(pk=pk)

            if qs.exists():
                raise ValidationError(
                    {"email": "A user with this email address already exists."})

        # 2. Birthday and minimum age validation (18+ years old)
        if self.birthday:
            today = timezone.localdate()
            if self.birthday > today:
                raise ValidationError(
                    {"birthday": "Birthday cannot be in the future."})

            try:
                min_age_date = self.birthday.replace(year=self.birthday.year + 18)
            except ValueError:
                min_age_date = self.birthday.replace(year=self.birthday.year + 18, day=28)

            if min_age_date > today:
                raise ValidationError(
                    {"birthday": "Users must be at least 18 years old to register."})

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

        return self.email