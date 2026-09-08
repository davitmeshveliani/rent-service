from django.db import models


class ListingManager(models.Manager):
    pass


class ReservationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("listing","user","listing__user",)


class ReviewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("listing","user","listing__user",)