import logging
from datetime import datetime, date
from typing import Tuple, Iterable

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import post_delete

from timeline.models import Entry

logger = logging.getLogger(__name__)


class BaseSource(models.Model):
    key = models.SlugField(max_length=80, primary_key=True)

    # Date range for this source's entries. This date range is inclusive (to <= date <= from).
    date_from = models.DateTimeField(null=True)
    date_until = models.DateTimeField(null=True)

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
        logger.info(f'Deleted {deleted_count} existing entries for source "{str(self)}"')
        return deleted_count

    def get_preprocessing_tasks(self) -> Iterable:
        return []

    def process(self, force=False) -> Tuple[int, int]:
        """
        Extract and create entries for this source
        """
        raise NotImplementedError

    def is_date_in_date_range(self, date: datetime):
        if self.date_from and date <= self.date_from:
            return False
        if self.date_until and date >= self.date_until:
            return False
        return True

    def is_entry_in_date_range(self, entry: Entry):
        return self.is_date_in_date_range(entry.date_on_timeline)

    def delete_entries_outside_date_range(self):
        total_deleted = 0
        if self.date_from:
            total_deleted += self.get_entries().filter(date_on_timeline__lt=self.date_from).delete()[0]
        if self.date_until:
            total_deleted += self.get_entries().filter(date_on_timeline__gt=self.date_until).delete()[0]

        if total_deleted > 0:
            range_message = f'Deleted {total_deleted} {str(self)} entries outside of date range '
            if self.date_from and self.date_until:
                range_message = f'({self.date_from.strftime("%Y-%m-%d %H:%M")} ' \
                                f'to {self.date_until.strftime("%Y-%m-%d %H:%M")})'
            elif self.date_from:
                range_message = f'(from {self.date_from.strftime("%Y-%m-%d %H:%M")})'
            elif self.date_until:
                range_message = f'(until {self.date_until.strftime("%Y-%m-%d %H:%M")})'
            logger.info(range_message)

    def get_postprocessing_tasks(self) -> Iterable:
        return [
            lambda force: self.delete_entries_outside_date_range()
        ]

    def clean(self):
        if self.date_from and self.date_until and self.date_from >= self.date_until:
            raise ValidationError('date_from must be smaller than date_until.')
