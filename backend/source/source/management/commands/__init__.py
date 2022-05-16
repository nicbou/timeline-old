import logging
from itertools import chain

from django.core.management import BaseCommand

from source.utils.models import get_models_by_name

logger = logging.getLogger(__name__)


class ModelProcessingCommand(BaseCommand):
    class_name = 'models'
    default_class = None

    def handle(self, *args, **options):
        class_names = options.get('classes_to_process') or [self.default_class.__name__]
        classes_to_process = get_models_by_name(class_names)
        if not classes_to_process:
            raise ValueError(f"No classes of types {class_names} found")

        logger.info(f"Processing {self.class_name} types: {[model.__name__ for model in classes_to_process]}")
        force_message = ' (with --force)' if options['force'] else ''

        instances_to_process = list(chain.from_iterable([c.objects.all() for c in classes_to_process]))

        preprocessing_tasks = set()
        postprocessing_tasks = set()

        for instance in instances_to_process:
            preprocessing_tasks.update(instance.get_preprocessing_tasks())
            postprocessing_tasks.update(instance.get_postprocessing_tasks())

        if len(preprocessing_tasks):
            logger.info(f"Running {len(preprocessing_tasks)} preprocessing tasks{force_message}")
        for task in preprocessing_tasks:
            task(force=options['force'])

        failure_count = 0
        for instance in instances_to_process:
            try:
                range_message = ''
                if instance.date_from and instance.date_until:
                    range_message = f' ({instance.date_from.strftime("%Y-%m-%d %H:%M")} ' \
                                    f'to {instance.date_until.strftime("%Y-%m-%d %H:%M")})'
                elif instance.date_from:
                    range_message = f' (from {instance.date_from.strftime("%Y-%m-%d %H:%M")})'
                elif instance.date_until:
                    range_message = f' (until {instance.date_from.strftime("%Y-%m-%d %H:%M")})'
                logger.info(f"Processing {instance}{range_message}{force_message}")
                self.process_instance(instance, force=options['force'])
            except KeyboardInterrupt:
                raise
            except:
                logger.exception(f"Failed to process {str(instance)}")
                failure_count += 1

        logger.info(f"{len(instances_to_process)} {self.class_name} instances processed. "
                    f"{len(instances_to_process) - failure_count} successful, {failure_count} failed.")

        if len(postprocessing_tasks):
            logger.info(f"Running {len(postprocessing_tasks)} postprocessing tasks{force_message}")
        for task in postprocessing_tasks:
            task(force=options['force'])

        logger.info(f"Finished processing all {self.class_name} instances")

    def process_instance(self, instance, force):
        return instance.process(force)

    def add_arguments(self, parser):
        parser.add_argument(
            'classes_to_process',
            nargs='*',
            type=str,
            help=f'One or more {self.class_name} class names to process. By default, all {self.class_name} types are '
                 'processed.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=f'Reprocess {self.class_name} instances that do not need to be processed.',
        )
