import logging
from typing import Tuple, Iterable

from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import post_delete

from timeline.models import Entry

logger = logging.getLogger(__name__)


class BaseSource(models.Model):
    key = models.SlugField(max_length=80, primary_key=True)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """
        Workaround because child classes don't inherit their parent's signals
        """
        super().__init_subclass__(**kwargs)
        post_delete.connect(cls.on_post_delete_signal, cls)

    @staticmethod
    def on_post_delete_signal(sender, instance: 'BaseSource', **kwargs):
        instance.post_delete()

    def post_delete(self):
        self.get_entries().delete()

    class Meta:
        abstract = True
        ordering = ['key']

    @property
    def source_name(self) -> str:
        return type(self).__name__

    @property
    def entry_source(self) -> str:
        """
        A "source" value shared by all entries created by this Source instance.
        For example "TwitterSource/katyperry" or "RsyncSource/macbook"
        """
        return f"{self.source_name}/{self.key}"

    def __str__(self) -> str:
        return self.entry_source

    def get_entries(self) -> QuerySet:
        return Entry.objects.filter(source=self.entry_source)

    def delete_entries(self):
        deleted_count = self.get_entries().delete()[0]
        logger.info(f'Deleted {deleted_count} existing entries for archive "{str(self)}"')
        return deleted_count

    def get_preprocessing_tasks(self) -> Iterable:
        return []

    def process(self, force=False) -> Tuple[int, int]:
        """
        Extract and create entries for this source
        """
        raise NotImplementedError

    def get_postprocessing_tasks(self) -> Iterable:
        return []

class OAuthSource(BaseSource):
    """
    Data source that requires OAuth capability to access information
    """
    consumer_key = models.CharField(max_length=100, blank=False)
    consumer_secret = models.CharField(max_length=100, blank=False)
    access_token = models.CharField(max_length=100, blank=True)
    refresh_token = models.CharField(max_length=100, blank=True)
    access_token_created = models.IntegerField(null=True)
    access_token_expires_in = models.IntegerField(null=True)

    class Meta:
        abstract = True
