from timeline.file_utils import generate_pdf_preview, generate_video_preview, generate_image_preview
from timeline.models import Entry
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generates previews and extends metadata for backup entries'

    # Note: we do incremental backups.
    # If we change image.png, there will be two versions of image.png on the server: before and after the change.
    # There will also be two entries: one for each version of image.png.
    # In other words, new files are added, but existing files don't change. If a file entry already has a checksum,
    # a mimetype, previews etc., we don't need to recalculate them. This saves us a lot of processing time.
    @staticmethod
    def get_previews_dir(entry: Entry, mkdir=False):
        previews_dir = (
                settings.PREVIEWS_ROOT /
                entry.extra_attributes.get('source', settings.DEFAULT_PREVIEW_SUBDIR) /
                entry.extra_attributes['checksum']
        )
        if mkdir:
            previews_dir.mkdir(parents=True, exist_ok=True)
        return previews_dir

    def set_pdf_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path'])
        entry.extra_attributes['previews'] = {}
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

    def set_image_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path'])
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

    def set_video_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path'])

        entry.extra_attributes['previews'] = {}
        for preview_name, preview_params in settings.VIDEO_PREVIEW_SIZES.items():
            preview_path = self.get_previews_dir(entry, mkdir=True) / f'{preview_name}.mp4'
            try:
                generate_video_preview(
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
                logger.exception(f'Could not generate video preview for entry #{entry.pk} ({str(original_path)}).')
                raise

    def get_processing_tasks(self, entry: Entry):
        tasks = []

        if entry.schema.startswith('file.image'):
            tasks.extend([
                self.set_image_previews,
            ])
        elif entry.schema.startswith('file.video'):
            tasks.extend([
                self.set_video_previews,
            ])
        elif entry.schema.startswith('file.document.pdf'):
            tasks.append(self.set_pdf_previews)

        return tasks

    def handle(self, *args, **options):
        entries = Entry.objects.filter(schema__startswith='file.')
        entry_count = len(entries)
        logger.info(f"Generating previews and metadata for {entry_count} file entries")
        missing_entry_count = 0
        for index, entry in enumerate(entries):
            entry_path = Path(entry.extra_attributes['path'])

            # This could happen if a Backup is deleted
            if not entry_path.exists():
                logger.error(f"Entry #{entry.id} does not exist at {entry.extra_attributes['path']}")
                missing_entry_count += 1
                entry.delete()
                continue

            logger.debug(f"Processing entry {index + 1}/{entry_count} (#{entry.id} - {entry.extra_attributes['path']})")
            for task in self.get_processing_tasks(entry):
                try:
                    task(entry)
                except:
                    logger.exception(f"Could not process entry #{entry.pk} "
                                     f"({ str(Path(entry.extra_attributes['path'])) }).")

            entry.save()

        if missing_entry_count == 0:
            logger.info(f"{len(entries)} file entries processed.")
        else:
            logger.warning(f"{len(entries)} file entries processed. "
                           f"{missing_entry_count} entries with missing files removed.")