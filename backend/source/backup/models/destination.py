import logging
from typing import Iterable

from django.db import models


logger = logging.getLogger(__name__)


class BaseDestination(models.Model):
    class Meta:
        abstract = True

    @property
    def destination_name(self) -> str:
        return type(self).__name__

    def __str__(self) -> str:
        return f"{self.destination_name}/{self.pk}"

    def get_preprocessing_tasks(self) -> Iterable:
        return []

    def get_postprocessing_tasks(self) -> Iterable:
        return []

    def process(self, force=False):
        raise NotImplementedError