import logging
from pathlib import Path
from typing import List, Callable

from django.conf import settings
from django.db import transaction

from backup.models.source import BaseSource
from timeline.models import Entry
from timeline.utils.files import generate_pdf_preview, generate_video_preview, generate_image_preview

logger = logging.getLogger(__name__)


def _get_previews_dir(entry: Entry, mkdir=False):
    previews_dir = (settings.PREVIEWS_ROOT / Path(entry.source) / entry.extra_attributes['file']['checksum'])
    if mkdir:
        previews_dir.mkdir(parents=True, exist_ok=True)
    return previews_dir


def _generate_pdf_previews(entry: Entry, overwrite=False):
    original_path = Path(entry.extra_attributes['file']['path'])
    entry.extra_attributes['previews'] = entry.extra_attributes.get('previews', {})

    for preview_name, preview_params in settings.DOCUMENT_PREVIEW_SIZES.items():
        preview_path = _get_previews_dir(entry, mkdir=True) / f'{preview_name}.png'
        try:
            generate_pdf_preview(
                original_path,
                preview_path,
                (preview_params['width'], preview_params['height']),
                overwrite=overwrite
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


def _generate_image_previews(entry: Entry, overwrite=False):
    original_path = Path(entry.extra_attributes['file']['path'])

    if 'width' not in entry.extra_attributes['media']:
        # Not a valid image
        return

    entry.extra_attributes['previews'] = {}
    for preview_name, preview_params in settings.IMAGE_PREVIEW_SIZES.items():
        preview_path = _get_previews_dir(entry, mkdir=True) / f'{preview_name}.jpg'
        try:
            generate_image_preview(
                original_path,
                preview_path,
                (preview_params['width'], preview_params['height']),
                overwrite=overwrite
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


def _generate_video_previews(entry: Entry, overwrite=False):
    original_path = Path(entry.extra_attributes['file']['path'])

    if 'duration' not in entry.extra_attributes['media']:
        # Not a valid video
        return

    entry.extra_attributes['previews'] = {}
    for preview_name, preview_params in settings.VIDEO_PREVIEW_SIZES.items():
        preview_path = _get_previews_dir(entry, mkdir=True) / f'{preview_name}.mp4'
        try:
            generate_video_preview(
                original_path,
                preview_path,
                video_duration=entry.extra_attributes['media']['duration'],
                max_dimensions=(preview_params['width'], preview_params['height']),
                overwrite=overwrite
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


def _original_file_exists(entry: Entry) -> bool:
    return Path(entry.extra_attributes['file']['path']).exists()


def _get_processing_tasks(entry: Entry) -> List[Callable[[Entry], None]]:
    tasks = []
    if entry.schema.startswith('file.image'):
        tasks.append(_generate_image_previews)
    elif entry.schema.startswith('file.video'):
        tasks.append(_generate_video_previews)
    elif entry.schema.startswith('file.document.pdf'):
        tasks.append(_generate_pdf_previews)
    return tasks


def generate_previews(source: BaseSource=None, force=False):
    """
    Generates previews on the timeline
    """
    entry_filters = {'schema__startswith': 'file.'}
    if source:
        entry_filters['source'] = source.entry_source

    entries = Entry.objects.filter(**entry_filters)

    entry_count = len(entries)
    log_message = f"Generating previews for {entry_count} entries"
    if source:
        log_message += f' from {source}'
    if force:
        log_message += ', and overwriting existing previews'

    logger.info(log_message)
    missing_entry_count = 0

    with transaction.atomic():
        for index, entry in enumerate(entries):
            # Delete orphaned entries (for example if the backup gets deleted)
            if not _original_file_exists(entry):
                logger.error(f"Entry #{entry.id} does not exist at {entry.extra_attributes['file']['path']}")
                missing_entry_count += 1
                entry.delete()
                continue

            logger.debug(f"Processing entry {index + 1}/{entry_count}"
                         f" (#{entry.id} - {entry.extra_attributes['file']['path']})")

            if processing_tasks := _get_processing_tasks(entry):
                logger.debug(f"Generating preview for {str(entry)} at {entry.extra_attributes['file']['path']}")
                for task in processing_tasks:
                    try:
                        task(entry, overwrite=force)
                    except:
                        logger.exception(f"Could not process entry #{entry.pk} "
                                         f"({ str(Path(entry.extra_attributes['file']['path'])) }).")
                entry.save()

        if missing_entry_count == 0:
            logger.info(f"{len(entries)} file entries processed.")
        else:
            logger.warning(f"{len(entries)} file entries processed, {missing_entry_count} orphaned entries removed")
