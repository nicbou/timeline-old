import logging
from typing import Tuple

from django.db import models


logger = logging.getLogger(__name__)


class BaseDestinationManager(models.Manager):
    def process(self, force=False):
        destinations = self.all()
        destination_count = destinations.count()
        logger.info(f"Processing {destination_count} destinations")
        failure_count = 0
        for destination in destinations:
            try:
                destination.process(force=force)
                logger.info(f"Processed destination {str(destination)}")
            except:
                logger.exception(f"Failed to process destination {str(destination)}")
                failure_count += 1
                pass
        logger.info(f"{destination_count} destinations processed. "
                    f"{destination_count - failure_count} successful, {failure_count} failed.")


class BaseDestination(models.Model):
    objects = BaseDestinationManager()

    class Meta:
        abstract = True

    @property
    def destination_name(self) -> str:
        return type(self).__name__

    def __str__(self) -> str:
        return f"{self.destination_name}/{self.pk}"

    def process(self, force=False):
        raise NotImplementedError