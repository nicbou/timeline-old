import logging

from source.management.commands import ModelProcessingCommand
from destination.models.destination import BaseDestination

logger = logging.getLogger(__name__)


class Command(ModelProcessingCommand):
    class_name = 'destination'
    default_class = BaseDestination
