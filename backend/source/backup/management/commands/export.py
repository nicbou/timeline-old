import logging

from backup.management.commands import ModelProcessingCommand
from backup.models.destination import BaseDestination

logger = logging.getLogger(__name__)


class Command(ModelProcessingCommand):
    class_name = 'destination'
    default_class = BaseDestination
