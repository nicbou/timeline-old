from timeline.file_utils import get_checksum, get_mimetype, generate_pdf_preview, generate_image_preview, \
    get_media_metadata, generate_video_preview
from timeline.models import Entry
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generates previews and extends metadata for backup entries'

    @staticmethod
    def set_file_mimetype(entry: Entry):
        if mimetype := get_mimetype(Path(entry.extra_attributes['path'])):
            entry.extra_attributes['mimetype'] = mimetype[0]

    @staticmethod
    def set_checksum(entry: Entry):
        entry.extra_attributes['checksum'] = get_checksum(Path(entry.extra_attributes['path']))

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

    @staticmethod
    def set_media_metadata(entry: Entry):
        original_path = Path(entry.extra_attributes['path'])
        try:
            original_media_attrs = get_media_metadata(original_path)
            entry.extra_attributes.update(original_media_attrs)
        except:
            logger.exception(f"Could not read metadata from video #{entry.pk} at {original_path}")

    def set_pdf_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path'])
        logger.info(f"Generating PDF previews for #{entry.pk} ({str(original_path)})")
        entry.extra_attributes['previews'] = {}
        for preview_name, preview_params in settings.IMAGE_PREVIEW_SIZES.items():
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

    def set_image_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path'])
        logger.info(f"Generating image previews for #{entry.pk} ({str(original_path)})")
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

    def set_video_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path'])

        logger.info(f"Generating video previews for #{entry.pk} ({str(original_path)})")

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

    def get_processing_tasks(self, entry: Entry):
        tasks = [
            self.set_file_mimetype,
            self.set_checksum,
        ]

        if entry.schema.startswith('file.image'):
            tasks.extend([
                self.set_media_metadata,
                self.set_image_previews,
            ])
        elif entry.schema.startswith('file.video'):
            tasks.append(self.set_video_previews)
        elif entry.schema.startswith('file.document.pdf'):
            tasks.append(self.set_pdf_previews)

        return tasks

    def handle(self, *args, **options):
        entries = Entry.objects.filter(schema__startswith='file.')
        logger.info(f"Generating previews and metadata for {len(entries)} file entries")
        for entry in entries:
            logger.info(f"Processing #{entry.id} ({entry.extra_attributes['path']})")
            for task in self.get_processing_tasks(entry):
                task(entry)

            entry.save()

        logger.info(f"Backup entries generated.")
