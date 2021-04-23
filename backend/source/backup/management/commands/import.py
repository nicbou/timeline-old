import logging

from backup.management.commands import ModelProcessingCommand
from backup.models.source import BaseSource

logger = logging.getLogger(__name__)


class Command(ModelProcessingCommand):
    class_name = 'source and archive'
    default_class = BaseSource
