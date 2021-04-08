import logging
from typing import List

from django.apps import apps
from django.core.management import BaseCommand

from backup.models.destination import BaseDestination
from backup.models.source import BaseSource


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    @staticmethod
    def get_classes_to_process(options: dict) -> List:
        """
        Return a list of classes to process. All supplied classes and their subclasses will be processed.
        """
        base_classes = [BaseSource, BaseDestination]
        if options['classes_to_process']:
            base_classes = [m for m in apps.get_models() if m.__name__ in options['classes_to_process']]
            if not base_classes:
                raise Exception(f"No classes of these types found: {options['classes_to_process']}")

        return [
            m for m in apps.get_models() if
            any(issubclass(m, base_class) for base_class in base_classes)
        ]

    def handle(self, *args, **options):
        """
        Process all instances of all sources/destinations
        """
        classes_to_process = self.get_classes_to_process(options)

        logger.info(f"Processing source/archive/destination types {[model.__name__ for model in classes_to_process]}")
        for class_to_process in classes_to_process:
            logger.info(f"Processing sources/archives/destinations of type {class_to_process.__name__}")
            class_to_process.objects.process(force=options['force'])
        logger.info(f"All source/archive/destination types processed")

    def add_arguments(self, parser):
        parser.add_argument(
            'classes_to_process',
            nargs='*',
            type=str,
            help='One or more source/archive/destination classes to process (e.g. "TwitterSource" or "TwitterArchive" '
                 'or "RsyncDestination"). By default, all source/archive/destination types are processed.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Reprocess sources, archives and destinations that do not need to be processed.',
        )
