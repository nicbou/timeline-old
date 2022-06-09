import logging
from pathlib import Path
from typing import List, Callable

from django.conf import settings
from django.db import transaction

from source.models.source import BaseSource
from timeline.models import Entry
from timeline.utils.files import generate_pdf_preview, generate_video_preview, generate_image_preview, \
    VideoDurationError

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

    if 'width' not in entry.extra_attributes.get('media', {}):
        logger.warning(f"Image entry #{entry.id} ({entry.extra_attributes['file']['path']}) does not have a width")
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

    if 'duration' not in entry.extra_attributes.get('media', {}):
        logger.warning(f"Video entry #{entry.id} ({entry.extra_attributes['file']['path']}) does not have a duration")
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
        except VideoDurationError as e:
            logger.debug(f'Could not generate video preview for entry #{entry.pk} ({str(original_path)}). {str(e)}')
            break  # Same error will happen for other preview sizes
        except KeyboardInterrupt:
            raise
        except:
            logger.exception(f'Could not generate video preview for entry #{entry.pk} ({str(original_path)}).')
            raise


def _get_preview_processing_tasks(entry: Entry) -> List[Callable[[Entry], None]]:
    tasks = []
    mimetype = entry.extra_attributes['file'].get('mimetype') or 'unknown'
    if mimetype.startswith('image/'):
        tasks.append(_generate_image_previews)
    elif mimetype.startswith('video/'):
        tasks.append(_generate_video_previews)
    elif mimetype == 'application/pdf':
        tasks.append(_generate_pdf_previews)
    elif mimetype.startswith('text/') or mimetype.startswith('audio/'):
        pass
    else:
        file_extension = Path(entry.extra_attributes['file']['path']).suffix
        logger.warning(f'Unrecognised mimetype for entry #{entry.pk}: {mimetype}. '
                       f'File extension: {file_extension}')
    return tasks


def generate_previews(source: BaseSource=None, force=False):
    """
    Generates previews on the timeline
    """
    entry_filters = {'extra_attributes__has_key': 'file'}
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
            if not Path(entry.extra_attributes['file']['path']).exists():
                logger.error(f"Entry #{entry.id} does not exist at {entry.extra_attributes['file']['path']}")
                missing_entry_count += 1
                entry.delete()
                continue

            logger.debug(f"Processing entry {index + 1}/{entry_count}"
                         f" (#{entry.id} - {entry.extra_attributes['file']['path']})")

            if processing_tasks := _get_preview_processing_tasks(entry):
                logger.debug(f"Generating preview for {str(entry)} at {entry.extra_attributes['file']['path']}")
                for task in processing_tasks:
                    try:
                        task(entry, overwrite=force)
                    except KeyboardInterrupt:
                        raise
                    except:
                        logger.exception(f"Could not generate preview for entry #{entry.pk} "
                                         f"({ str(Path(entry.extra_attributes['file']['path'])) }).")
                entry.save()

        if missing_entry_count == 0:
            logger.info(f"Generated previews for {len(entries)} entries.")
        else:
            logger.warning(f"Generated previews for {len(entries)} entries, "
                           f"{missing_entry_count} orphaned entries removed")
