from django.db import models


class BackupSource(models.Model):
    user = models.CharField(max_length=80)
    host = models.CharField(max_length=255)
    port = models.PositiveSmallIntegerField(default=22)
    path = models.TextField()