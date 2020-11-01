import hashlib
import json
import logging
import mimetypes
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def get_mimetype(file_path: Path) -> str:
    return mimetypes.guess_type(file_path, strict=False)[0]


def get_checksum(file_path: Path):
    with open(file_path, "rb") as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def generate_pdf_preview(input_path: Path, output_path: Path, max_dimensions: (int, int), overwrite=False):
    return generate_image_preview(input_path, output_path, max_dimensions, overwrite)


def get_media_metadata(input_path: Path):
    ffprobe_cmd = subprocess.run(
        [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=width,height,duration,codec_name',
            '-of', 'json',
            str(input_path)
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    raw_metadata = json.loads(ffprobe_cmd.stdout.decode('utf-8'))['streams'][0]

    metadata = {
        'width': int(raw_metadata['width']),
        'height': int(raw_metadata['height']),
    }

    if 'duration' in raw_metadata:
        metadata['duration'] = int(float(raw_metadata['duration']))  # Note: images can also have a duration
    if 'codec_name' in raw_metadata:
        metadata['codec_name'] = raw_metadata['codec_name']

    return metadata


def generate_video_preview(input_path: Path, output_path: Path, max_dimensions: (int, int), overwrite=False):
    if output_path.exists() and not overwrite:
        raise FileExistsError

    try:
        video_duration = int(get_media_metadata(input_path)['duration'])
    except:
        raise Exception(f"Could not read video metadata from {input_path}")

    try:
        sample_count = 10
        sample_duration = 2
        if video_duration <= 10:
            sample_count = 1
            sample_duration = video_duration
        elif video_duration <= 30:
            sample_count = 5
            sample_duration = 1
        elif video_duration <= 5 * 60:
            sample_count = 5
            sample_duration = 2

        # Take a [sample_duration] video sample at every 1/[sample_count] of the video
        preview_intervals = [
            (sample_start, sample_start + sample_duration)
            for sample_start in [
                int(i / sample_count * video_duration)
                for i in range(0, sample_count)
            ]
        ]

        # Cut the sample
        ffmpeg_filter = " ".join(
            f"[0:v]trim={start}:{end},setpts=PTS-STARTPTS[v{index}];"
            for index, (start, end) in enumerate(preview_intervals)  # noqa
        )

        # Concatenate the samples
        ffmpeg_filter += "".join(
            f"[v{i}]" for i in range(0, len(preview_intervals))
        )
        ffmpeg_filter += f"concat=n={sample_count}:v=1[allclips];"

        # Scale the output to fit max size, but don't enlarge, don't crop, and don't change aspect ratio
        ffmpeg_filter += \
            f"[allclips]scale=ceil(iw*min(1\\,min({max_dimensions[0]}/iw\\,{max_dimensions[1]}/ih))/2)*2:-2[out]"

        command = [
            'ffmpeg',
            '-i', str(input_path),
            '-filter_complex', ffmpeg_filter,
            '-map', '[out]',
            '-codec:v', 'libx264',
            '-profile:v', 'baseline',
            '-level', '3.0',
            '-preset', 'slow',
            '-threads', '0',
            '-movflags', '+faststart',
            str(output_path),
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as exc:
        command = " ".join(exc.cmd)
        raise Exception(
            f'Could not generate video preview.\n'
            f"FFMPEG COMMAND:\n{command}\n"
            f"FFMPEG OUTPUT:\n{exc.stderr.decode('UTF-8')}"
        )


def generate_image_preview(input_path: Path, output_path: Path, max_dimensions: (int, int), overwrite=False):
    if output_path.exists() and not overwrite:
        raise FileExistsError

    try:
        command = [
            'convert',
            '-thumbnail', f"{max_dimensions[0]}x{max_dimensions[1]}>",
            f"{str(input_path)}[0]",
            str(output_path),
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as exc:
        command = " ".join(exc.cmd)
        raise Exception(
            f'Could not generate image preview.\n'
            f"IMAGEMAGICK COMMAND:\n{command}\n"
            f"IMAGEMAGICK OUTPUT:\n{exc.stderr.decode('UTF-8')}"
        )