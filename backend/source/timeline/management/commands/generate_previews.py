import logging
from pathlib import Path
from typing import List, Callable

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from timeline.file_utils import generate_pdf_preview, generate_video_preview, generate_image_preview
from timeline.models import Entry

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generates previews and extends metadata for backup entries'

    # Note: we do incremental backups.
    # - If we change image.png, there will be two versions of image.png on the server: before and after the change.
    #   There will also be two entries: one for each version of image.png. New files are added, but existing files don't
    #   change.
    # - We use the file checksum to name previews, so multiple identical files will have the same previews.

    @staticmethod
    def get_previews_dir(entry: Entry, mkdir=False):
        previews_dir = (
                settings.PREVIEWS_ROOT /
                Path(entry.source) /
                entry.extra_attributes['file']['checksum']
        )
        if mkdir:
            previews_dir.mkdir(parents=True, exist_ok=True)
        return previews_dir

    def generate_pdf_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['file']['path'])
        entry.extra_attributes['previews'] = entry.extra_attributes.get('previews', {})

        for preview_name, preview_params in settings.DOCUMENT_PREVIEW_SIZES.items():
            preview_path = self.get_previews_dir(entry, mkdir=True) / f'{preview_name}.png'
            try:
                generate_pdf_preview(
                    original_path,
                    preview_path,
                    (preview_params['width'], preview_params['height']),
                    overwrite=False
                )
                entry.extra_attributes['previews'][preview_name] = str(preview_path)
            except FileExistsError:
                logger.debug(f'"{preview_name}" preview for #{entry.pk} already exists.')
                entry.extra_attributes['previews'][preview_name] = str(preview_path)
            except KeyboardInterrupt:
                raise
            except:
                logger.exception(f'Could not generate PDF preview for entry #{entry.pk} ({str(original_path)}).')
                raise

    def generate_image_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['file']['path'])

        if 'width' not in entry.extra_attributes['media']:
            # Not a valid image
            return

        entry.extra_attributes['previews'] = {}
        for preview_name, preview_params in settings.IMAGE_PREVIEW_SIZES.items():
            preview_path = self.get_previews_dir(entry, mkdir=True) / f'{preview_name}.jpg'
            try:
                generate_image_preview(
                    original_path,
                    preview_path,
                    (preview_params['width'], preview_params['height']),
                    overwrite=False
                )
                entry.extra_attributes['previews'][preview_name] = str(preview_path)
            except FileExistsError:
                logger.debug(f'"{preview_name}" preview for #{entry.pk} already exists.')
                entry.extra_attributes['previews'][preview_name] = str(preview_path)
            except KeyboardInterrupt:
                raise
            except:
                logger.exception(f'Could not generate image preview for entry #{entry.pk} ({str(original_path)}).')
                raise

    def generate_video_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['file']['path'])

        if 'duration' not in entry.extra_attributes['media']:
            # Not a valid video
            return

        entry.extra_attributes['previews'] = {}
        for preview_name, preview_params in settings.VIDEO_PREVIEW_SIZES.items():
            preview_path = self.get_previews_dir(entry, mkdir=True) / f'{preview_name}.mp4'
            try:
                generate_video_preview(
                    original_path,
                    preview_path,
                    video_duration=entry.extra_attributes['media']['duration'],
                    max_dimensions=(preview_params['width'], preview_params['height']),
                    overwrite=False
                )
                entry.extra_attributes['previews'][preview_name] = str(preview_path)
            except FileExistsError:
                logger.debug(f'"{preview_name}" preview for #{entry.pk} already exists.')
                entry.extra_attributes['previews'][preview_name] = str(preview_path)
            except ValueError as e:
                logger.exception(f'Could not generate video preview for entry #{entry.pk} ({str(original_path)}). {str(e)}')
            except KeyboardInterrupt:
                raise
            except:
                logger.exception(f'Could not generate video preview for entry #{entry.pk} ({str(original_path)}).')
                raise

    @staticmethod
    def original_file_exists(entry: Entry) -> bool:
        return Path(entry.extra_attributes['file']['path']).exists()

    def get_processing_tasks(self, entry: Entry) -> List[Callable[[Entry], None]]:
        tasks = []
        if entry.schema.startswith('file.image'):
            tasks.append(self.generate_image_previews)
        elif entry.schema.startswith('file.video'):
            tasks.append(self.generate_video_previews)
        elif entry.schema.startswith('file.document.pdf'):
            tasks.append(self.generate_pdf_previews)
        return tasks

    def handle(self, *args, **options):
        entries = Entry.objects.filter(schema__startswith='file.')

        entry_count = len(entries)
        logger.info(f"Generating previews and metadata for {entry_count} file entries")
        missing_entry_count = 0

        with transaction.atomic():
            for index, entry in enumerate(entries):
                # Delete orphaned entries (for example if the backup gets deleted)
                if not self.original_file_exists(entry):
                    logger.error(f"Entry #{entry.id} does not exist at {entry.extra_attributes['file']['path']}")
                    missing_entry_count += 1
                    entry.delete()
                    continue

                logger.debug(f"Processing entry {index + 1}/{entry_count}"
                             f" (#{entry.id} - {entry.extra_attributes['file']['path']})")

                if processing_tasks := self.get_processing_tasks(entry):
                    for task in processing_tasks:
                        try:
                            task(entry)
                        except:
                            logger.exception(f"Could not process entry #{entry.pk} "
                                             f"({ str(Path(entry.extra_attributes['file']['path'])) }).")
                    entry.save()

            if missing_entry_count == 0:
                logger.info(f"{len(entries)} file entries processed.")
            else:
                logger.warning(f"{len(entries)} file entries processed, {missing_entry_count} orphaned entries removed")
