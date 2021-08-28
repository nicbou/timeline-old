import json
import logging
from collections import Generator
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Iterable

import pytz
from django.db import models

from archive.models.base import CompressedFileArchive, archive_path
from backup.utils.files import entry_from_file_path
from timeline.models import Entry
from timeline.utils.postprocessing import generate_previews

logger = logging.getLogger(__name__)


class FacebookArchive(CompressedFileArchive):
    """
    Reads Facebook data exports
    """
    keep_extracted_files = True

    def extract_entries(self) -> Generator[Entry, None, None]:
        messages_root = self.extracted_files_path / 'messages'
        message_dirs = (
            messages_root / 'archived_threads',
            messages_root / 'filtered_threads',
            messages_root / 'inbox'
        )

        for message_dir in message_dirs:
            files = list(message_dir.glob('**/message_*.json'))
            for index, file in enumerate(files):
                logger.info(
                    f"Processing {index + 1}/{len(files)} message files in '{message_dir.name}': "
                    f"{file.parent.name}/{file.name}"
                )
                yield from self.extract_messages_from_file(file)

    def extract_messages_from_file(self, json_file_path: Path) -> Entry:
        with json_file_path.open() as json_file:
            json_data = json.load(json_file)

        chat_participants = json_data['participants']
        if len(chat_participants) == 1:
            # If someone blocks you, you are the only participant in the chat
            # We add a new participant named after the directory, so just a hash like "cjd8jaswzw"
            chat_participants.append(json_file_path.parent.name)

        total = 0
        for message in json_data['messages']:
            if not message['is_unsent']:
                total += 1
                try:
                    yield from self.entries_from_message(
                        message,
                        chat_title=json_data['title'],
                        chat_participants=chat_participants
                    )
                except KeyboardInterrupt:
                    raise
                except:
                    logging.exception(f"Could not read message in {str(json_file_path)}: {message}")

        logger.info(f"Processed {total} messages.")

    @staticmethod
    def message_date(message: dict) -> datetime:
        return pytz.utc.localize(datetime.fromtimestamp(message['timestamp_ms'] / 1000.0))

    def entries_from_message(self, message: dict, chat_title: str, chat_participants: Iterable) -> Entry:
        sender = message['sender_name']
        recipient = None

        if message['sender_name'] != chat_title:
            # if it's from you to the other participant, or from any participant to a group chat
            recipient = chat_title
        else:
            # otherwise, it's an inbound message in a 2 person chat
            assert len(list(chat_participants)) == 2
            for participant in chat_participants:
                if participant != message['sender_name']:
                    recipient = participant

        assert recipient is not None

        if message['type'] == 'Call':
            return Entry(
                source=self.entry_source,
                schema='call.facebook',
                title='',
                description='',
                extra_attributes={
                    'caller1_name': sender,
                    'caller1_id': sender,
                    'caller2_name': recipient,
                    'caller2_id': recipient,
                    'duration': message['call_duration'],
                },
                date_on_timeline=self.message_date(message),
            )
        else:
            message_date = self.message_date(message)
            message_metadata = {
                'sender_name': sender, 'sender_id': sender,
                'recipient_name': recipient, 'recipient_id': recipient,
            }

            # Each photo/video/audio/gif in a message is a distinct Entry
            for video in message.get('videos', []):
                yield self.entry_from_attachment(
                    schema='message.facebook.video',
                    file_path=video['uri'],
                    date_on_timeline=message_date,
                    extra_attributes=message_metadata
                )

            for photo in message.get('photos', []):
                yield self.entry_from_attachment(
                    schema='message.facebook.image',
                    file_path=photo['uri'],
                    date_on_timeline=message_date,
                    extra_attributes=message_metadata
                )

            for file in message.get('files', []):
                yield self.entry_from_attachment(
                    schema='message.facebook.file',
                    file_path=file['uri'],
                    date_on_timeline=message_date,
                    extra_attributes=message_metadata
                )

            for gif in message.get('gifs', []):
                yield self.entry_from_attachment(
                    schema='message.facebook.gif',
                    file_path=gif['uri'],
                    date_on_timeline=message_date,
                    extra_attributes=message_metadata
                )

            for audio in message.get('audio_files', []):
                yield self.entry_from_attachment(
                    schema='message.facebook.audio',
                    file_path=audio['uri'],
                    date_on_timeline=message_date,
                    extra_attributes=message_metadata
                )

            if "sticker" in message:
                yield self.entry_from_attachment(
                    schema='message.facebook.sticker',
                    file_path=message['sticker']['uri'],
                    date_on_timeline=message_date,
                    extra_attributes=message_metadata
                )

            if message.get('content'):
                yield Entry(
                    source=self.entry_source,
                    schema='message.facebook',
                    title='',
                    description=message['content'],
                    date_on_timeline=message_date,
                    extra_attributes=message_metadata,
                )

    def entry_from_attachment(self, file_path: Path, schema: str, date_on_timeline: datetime, extra_attributes: dict):
        entry = entry_from_file_path(self.extracted_files_path / file_path, self)
        entry.schema = schema
        entry.extra_attributes.update(extra_attributes)
        entry.date_on_timeline = date_on_timeline
        return entry

    def get_postprocessing_tasks(self):
        return [
            partial(generate_previews, source=self),
        ]