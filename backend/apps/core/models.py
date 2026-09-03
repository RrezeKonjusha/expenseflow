from django.db import models
from django.db.models.functions import Now


class BaseModel(models.Model):
    """Abstract entity: every table gets audit timestamps.

    `updated_at` is also maintained by the `trg_touch_updated_at` trigger,
    so rows changed by raw SQL (stored procedure) stay correct.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        abstract = True
