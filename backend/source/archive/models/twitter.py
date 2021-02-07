import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytz

from archive.models.base import BaseArchive
from timeline.models import Entry

logger = logging.getLogger(__name__)


def remove_twitter_js(input_path: Path, output_path: Path):
    """
    The files are not JSON files, but JavaScript files. They're just a big JS object assigned to a variable. If we
    replace the first line, we get valid JSON.
    """
    with input_path.open('r') as input_file, output_path.open('w') as output_file:
        input_file.readline()  # Discard the first line, "window.YTD.tweet.part0 = [ {"
        output_file.write('[ {')
        shutil.copyfileobj(input_file, output_file)  # Write rest of file


def twitter_date_to_datetime(twitter_date: str) -> datetime:
    return datetime.strptime(twitter_date, '%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC)


class TwitterArchive(BaseArchive):
    source_name = 'twitter'

    def get_account_info(self):
        js_file = self.files_path / 'data/account.js'
        json_file = self.files_path / 'data/account.json'
        remove_twitter_js(js_file, json_file)

        with json_file.open(encoding='utf-8') as json_file_handle:
            return json.load(json_file_handle)[0]['account']

    def extract_entries(self) -> Generator[Entry, None, None]:
        account_info = self.get_account_info()

        js_file_path = self.files_path / 'data/tweet.js'
        json_file_path = self.files_path / 'data/tweet.json'
        remove_twitter_js(js_file_path, json_file_path)

        with json_file_path.open('r', encoding='utf-8') as json_file:
            json_entries = [t['tweet'] for t in json.load(json_file)]

            logger.info(f"Adding tweets found in {str(json_file_path)}")
            for tweet in json_entries:
                entry = Entry(
                    schema='social.twitter.tweet',
                    title='',
                    description=tweet['full_text'],
                    date_on_timeline=twitter_date_to_datetime(tweet['created_at']),
                    extra_attributes={
                        "post_id": tweet['id'],
                        "post_user": account_info['username'],
                        "source": self.entry_source,
                    },
                    source=self.entry_source,
                )

                if tweet.get('in_reply_to_status_id'):
                    entry.extra_attributes['post_parent_id'] = tweet['in_reply_to_status_id']

                yield entry
