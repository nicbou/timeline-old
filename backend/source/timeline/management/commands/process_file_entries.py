from timeline.models import Entry
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path
import hashlib
import json
import logging
import mimetypes
import subprocess

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generates previews and extends metadata for backup entries'

    def set_file_mimetype(self, entry: Entry):
        mimetype = mimetypes.guess_type(entry.extra_attributes['path'], strict=False)
        if mimetype:
            entry.extra_attributes['mimetype'] = mimetype[0]

    def get_media_attributes(self, file_path: Path):
        ffprobe_cmd = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'stream=width,height,duration,nb_frames,codec_name',
                '-of', 'json',
                str(file_path.resolve())
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return json.loads(ffprobe_cmd.stdout.decode('utf-8'))['streams'][0]

    def set_file_checksum(self, entry: Entry):
        with open(Path(entry.extra_attributes['path']).resolve(), "rb") as f:
            file_hash = hashlib.blake2b()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        entry.extra_attributes['checksum'] = file_hash.hexdigest()

    def set_image_exif(self, entry: Entry):
        pass

    def get_previews_dir(self, entry: Entry, mkdir=False):
        previews_dir = (
            settings.PREVIEWS_ROOT /
            entry.extra_attributes.get('source', settings.DEFAULT_PREVIEW_SUBDIR) /
            entry.extra_attributes['checksum']
        )
        if mkdir:
            previews_dir.mkdir(parents=True, exist_ok=True)
        return previews_dir

    def set_pdf_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path']).resolve()

        logger.info(f"Generating PDF previews for #{entry.id} ({str(original_path)})")

        entry.extra_attributes['previews'] = {}
        for preview_name, preview_params in settings.IMAGE_PREVIEW_SIZES.items():
            preview_path = (self.get_previews_dir(entry, mkdir=True) / f'{preview_name}.png').resolve()

            if preview_path.exists():
                logger.info(f'"{preview_name}" preview for #{entry.id} already exists.')
            else:
                try:
                    subprocess.run(
                        [
                            'convert',
                            '-resize', f"x{preview_params['height']}",
                            f"{str(original_path)}[0]",
                            str(preview_path),
                        ],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        check=True,
                    )
                except subprocess.CalledProcessError as exc:
                    logger.error(f'Could not generate preview for entry #{entry.id} ({str(original_path)}).\nimagemagick output:\n{exc.stderr}')

            entry.extra_attributes['previews'][preview_name] = str(preview_path)

    def set_image_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path']).resolve()

        try:
            original_media_attrs = self.get_media_attributes(original_path)
        except:
            logger.exception(f"Could not read metadata from video #{entry.id} at {original_path}")
            return

        if 'width' not in original_media_attrs or 'height' not in original_media_attrs:
            logger.error('Image has no width or height, ignoring.')
            return

        entry.extra_attributes['width'] = int(original_media_attrs['width'])
        entry.extra_attributes['height'] = int(original_media_attrs['height'])

        logger.info(f"Generating image previews for #{entry.id} ({str(original_path)})")

        entry.extra_attributes['previews'] = {}
        for preview_name, preview_params in settings.IMAGE_PREVIEW_SIZES.items():
            preview_path = (self.get_previews_dir(entry, mkdir=True) / f'{preview_name}.jpg').resolve()

            # Only generate previews if they're smaller than the original
            if preview_params['height'] < entry.extra_attributes['height']:
                if preview_path.exists():
                    logger.info(f'"{preview_name}" preview for #{entry.id} already exists.')
                else:
                    try:
                        subprocess.run(
                            [
                                'convert',
                                '-resize', f"x{preview_params['height']}",
                                f"{str(original_path)}[0]",
                                str(preview_path),
                            ],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=True,
                        )
                    except subprocess.CalledProcessError as exc:
                        logger.error(f'Could not generate preview for entry #{entry.id} ({str(original_path)}).\nimagemagick output:\n{exc.stderr}')
            else:
                logger.info(f'"{preview_name}" preview is smaller than original. Skipping.')
                preview_path = original_path

            entry.extra_attributes['previews'][preview_name] = str(preview_path)

    def set_video_previews(self, entry: Entry):
        original_path = Path(entry.extra_attributes['path']).resolve()

        try:
            original_media_attrs = self.get_media_attributes(original_path)
        except:
            logger.exception(f"Could not read metadata from video #{entry.id} at {original_path}")
            return

        try:
            entry.extra_attributes['width'] = int(original_media_attrs['width'])
            entry.extra_attributes['height'] = int(original_media_attrs['height'])
            entry.extra_attributes['frames'] = int(original_media_attrs['nb_frames'])
            entry.extra_attributes['duration'] = original_media_attrs['duration']
            entry.extra_attributes['codec'] = original_media_attrs['codec_name']
        except:
            logger.error('Video is missing attributes, ignoring.')
            return

        logger.info(f"Generating video previews for #{entry.id} ({str(original_path)})")

        entry.extra_attributes['previews'] = {}
        for preview_name, preview_params in settings.VIDEO_PREVIEW_SIZES.items():
            preview_path = (self.get_previews_dir(entry, mkdir=True) / f'{preview_name}.jpg').resolve()

            if preview_path.exists():
                logger.info(f'"{preview_name}" preview for #{entry.id} already exists.')
            else:
                try:
                    preview_frame_count = 10
                    frame_interval = entry.extra_attributes['frames'] // preview_frame_count
                    subprocess.run(
                        [
                            'ffmpeg',
                            '-y',
                            '-i', str(original_path),
                            '-frames', '1',
                            '-q:v', '1',
                            '-vf', f"select=not(mod(n\,{frame_interval})),scale=-1:{preview_params['height']},tile={preview_frame_count}x1",
                            str(preview_path),
                        ],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        check=True,
                    )
                except subprocess.CalledProcessError as exc:
                    logger.error(f'Could not generate preview for entry #{entry.id} ({str(original_path)}).\nffmpeg output:\n{exc.stderr}')

            entry.extra_attributes['previews'][preview_name] = str(preview_path)

    def get_processing_tasks(self, entry: Entry):
        tasks = [
            self.set_file_mimetype,
            self.set_file_checksum,
        ]

        if entry.schema.startswith('file.image'): 
            tasks.extend([
                self.set_image_exif,
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