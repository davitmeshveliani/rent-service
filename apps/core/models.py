import uuid

from django.db import models


class UUIDAbstractModel(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)

    class Meta:
        abstract = True


class TimeStampedUUIDModel(UUIDAbstractModel):
    created_at = models.DateTimeField(auto_now_add=True,db_index=True,)

    class Meta:
        abstract = True
        ordering = ["-created_at"]