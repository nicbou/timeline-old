import logging

from backup.management.commands import ModelProcessingCommand
from backup.models.destination import BaseDestination

logger = logging.getLogger(__name__)


class Command(ModelProcessingCommand):
    default_class = BaseDestination
