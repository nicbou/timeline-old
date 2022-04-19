import json
import logging
from typing import Generator
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Optional

import pytz
from django.db import models

from archive.models.base import CompressedFileArchive
from source.utils.files import entry_from_file_path
from timeline.models import Entry
from timeline.utils.postprocessing import generate_previews

logger = logging.getLogger(__name__)


class TelegramArchive(CompressedFileArchive):
    """
    Reads Telegram Desktop exports
    """
    keep_extracted_files = True  # The archive contains message attachments

    include_supergroup_chats = models.BooleanField("Include supergroup chats", default=False)
    include_group_chats = models.BooleanField("Include group chats", default=True)

    def extract_entries(self) -> Generator[Entry, None, None]:
        json_path = self.extracted_files_path / 'result.json'
        assert json_path.exists(), "Could not find result.json at the root of the Telegram archive."
        with json_path.open() as json_file:
            json_data = json.load(json_file)

        account = json_data['personal_information']
        for index, chat in enumerate(chats := json_data['chats']['list']):
            logger.info(f"Processing {index + 1}/{len(chats)} chats: {chat['name']} ({len(chat['messages'])} messages)")
            if chat['type'] == 'private_supergroup' and not self.include_supergroup_chats:
                logger.info(f"Ignored chat \"{chat['name']}\" because supergroup chats are ignored")
            elif chat['type'] == 'private_group' and not self.include_group_chats:
                logger.info(f"Ignored chat \"{chat['name']}\" because group chats are ignored")
            else:
                for message in chat['messages']:
                    if message.get('action') == 'phone_call':
                        yield self.entry_from_call(account, chat, message)
                    elif message.get('type') == 'message':
                        yield self.entry_from_message(account, chat, message)

    def get_postprocessing_tasks(self):
        return [
            partial(generate_previews, source=self),
        ]

    @staticmethod
    def account_name(account_info: dict) -> str:
        return f"{account_info['first_name'].strip()} {account_info['last_name'].strip()}".strip()

    @staticmethod
    def account_id(account_info: dict) -> str:
        return f"user{account_info['user_id']}"

    def get_message_file_path(self, message: dict) -> Optional[Path]:
        relative_path = message.get('photo') or message.get('file')
        if not relative_path:
            return None

        absolute_path = self.extracted_files_path / relative_path
        if not absolute_path.exists():
            # If the archive was created with MacOS, the file names are Unicode, but Python reads them as CP437. This
            # breaks file names with unicode characters in them. Blame OSX, which does not set bit 11 to mark ZIPs as
            # unicode.
            absolute_path = self.extracted_files_path / str(relative_path).encode().decode('cp437')

        if not absolute_path.exists():
            if relative_path.startswith("(File not included"):
                logger.debug(f"Message file {message['id']} is not in the archive. It might be a reaction GIF.")
            else:
                logger.warning(f"Message file at {str(absolute_path)} does not exist.")
            return None

        return absolute_path

    @staticmethod
    def get_message_date(message: dict) -> datetime:
        return pytz.utc.localize(datetime.strptime(message['date'], "%Y-%m-%dT%H:%M:%S"))

    @staticmethod
    def get_message_text(message: dict) -> str:
        if type(message.get('text')) is str:
            if message.get('media_type') == 'sticker':
                text = message.get('sticker_emoji', '[sticker]')
            elif message.get('media_type') == 'animation':
                text = '[reaction GIF]'
            else:
                text = message.get('text', '')
        else:
            text = ''
            for fragment in message['text']:
                if type(fragment) is str:
                    text += fragment
                elif fragment.get('text'):
                    text += fragment['text']
                else:
                    logger.warning(f"Invalid fragment: {fragment}")

        return text

    def entry_from_message(self, account: dict, chat: dict, message: dict) -> Entry:
        if file := self.get_message_file_path(message):
            entry = entry_from_file_path(file, self)
            mimetype = entry.extra_attributes['file']['mimetype']
            if mimetype and mimetype.startswith('audio'):
                entry.schema = 'message.telegram.audio'
            elif mimetype and mimetype.startswith('video'):
                entry.schema = 'message.telegram.video'
            elif mimetype and mimetype.startswith('image'):
                entry.schema = 'message.telegram.image'
        else:
            entry = Entry()
            if message.get('media_type') == 'sticker':
                entry.schema = 'message.telegram.sticker'
            elif message.get('media_type') == 'animation':
                entry.schema = 'message.telegram.gif'
            else:
                entry.schema = 'message.telegram'

        entry.source = self.entry_source
        entry.description = self.get_message_text(message)
        entry.date_on_timeline = self.get_message_date(message)

        # Set message metadata
        if chat['type'] == 'personal_chat':
            # For personal chats, messages are from one user to another user.
            # In the telegram data, the chat ID is the same as the other user's ID.
            if message['from_id'] == self.account_id(account):  # Outgoing private msg
                entry.extra_attributes.update({
                    'sender_name': self.account_name(account),
                    'sender_id': message['from_id'],
                    'recipient_name': chat['name'],
                    'recipient_id': message['from_id'],
                })
            else:  # Incoming private msg
                entry.extra_attributes.update({
                    'sender_name': message['from'],
                    'sender_id': message['from_id'],
                    'recipient_name': self.account_name(account),
                    'recipient_id': self.account_id(account),
                })
        else:
            # For group chats, messages are from one user to the rest of the group
            entry.extra_attributes.update({
                'sender_name': message['from'],
                'sender_id': message['from_id'],
                'recipient_name': chat['name'],
                'recipient_id': chat['id'],
            })

        return entry

    def entry_from_call(self, account: dict, chat: dict, message: dict) -> Entry:
        if message['actor_id'] == self.account_id(account):  # Outgoing call
            caller1 = {'name': message['actor'], 'id': message['actor_id']}
            caller2 = {'name': chat['name'], 'id': f"user{chat['id']}"}  # The chat ID is the other user's ID
        else:  # Incoming call
            caller1 = {'name': self.account_name(account), 'id': self.account_id(account)}
            caller2 = {'name': message['actor'], 'id': message['actor_id']}

        return Entry(
            source=self.entry_source,
            schema='call.telegram',
            title='',
            description='',
            extra_attributes={
                'duration': message.get('duration_seconds', 0),  # Not set for failed calls
                'caller1_name': caller1['name'],
                'caller1_id': caller1['id'],
                'caller2_name': caller2['name'],
                'caller2_id': caller2['id'],
            },
            date_on_timeline=self.get_message_date(message),
        )
