import logging
from typing import List

from django.apps import apps
from django.core.management import BaseCommand

from backup.models.base import BaseSource


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def get_source_classes(self, options: dict) -> List:
        """
        Return a list of classes to process. All supplied classes and their subclasses will be processed.
        """
        base_classes = [BaseSource, ]
        if options['source_classes']:
            base_classes = [m for m in apps.get_models() if m.__name__ in options['source_classes']]
            if not base_classes:
                raise Exception(f"No classes of these types found: {options['source_classes']}")

        return [
            m for m in apps.get_models() if
            any(issubclass(m, base_class) for base_class in base_classes)
        ]

    def handle(self, *args, **options):
        """
        Process all instances of all sources
        """
        source_classes = self.get_source_classes(options)

        logger.info(f"Processing source types {[model.__name__ for model in source_classes]}")
        for source_class in source_classes:
            logger.info(f"Processing sources of type {source_class.__name__}")
            source_class.objects.process(force=options['force'])
        logger.info(f"All source types processed")

    def add_arguments(self, parser):
        parser.add_argument(
            'source_classes',
            nargs='*',
            type=str,
            help='One or more source classes to process (e.g. "TwitterSource" or "TwitterArchive"). By default, '
                 'all sources classes are processed.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Reprocess sources and archives that do not need to be processed.',
        )
