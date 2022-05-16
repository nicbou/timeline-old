from django.db import models

from source.models.source import BaseSource


class OAuthSource(BaseSource):
    """
    Data source that requires OAuth capability to access information
    """
    consumer_key = models.CharField(max_length=100, blank=False)
    consumer_secret = models.CharField(max_length=100, blank=False)
    access_token = models.CharField(max_length=100, blank=True)
    refresh_token = models.CharField(max_length=100, blank=True)
    access_token_created = models.DateTimeField(null=True)
    access_token_expires = models.DateTimeField(null=True)

    class Meta:
        abstract = True
