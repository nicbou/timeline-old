from django.db import models


class BackupSource(models.Model):
    user = models.CharField(max_length=80)
    host = models.CharField(max_length=255)
    port = models.PositiveSmallIntegerField(default=22)
    path = models.TextField()
    key = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.key} ({self.user}@{self.host}:{self.port}, {self.path})"