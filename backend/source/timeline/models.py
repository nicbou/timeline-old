from django.db import models
from django.utils import timezone


class Entry(models.Model):
    date_on_timeline = models.DateTimeField(default=timezone.now)

    schema = models.CharField(max_length=100)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    extra_attributes = models.JSONField(blank=True, default=dict)
