from django.db import models


class BackupSource(models.Model):
    user = models.CharField(max_length=80, blank=False)
    host = models.CharField(max_length=255, blank=False)
    port = models.PositiveSmallIntegerField(default=22)
    path = models.TextField(blank=False)
    key = models.CharField(max_length=80, blank=False)

    def __str__(self):
        return f"{self.key} ({self.user}@{self.host}:{self.port}, {self.path})"