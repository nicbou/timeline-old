import codecs
import csv
import logging
from typing import Generator
from datetime import datetime
from decimal import Decimal

import pytz

from archive.models.base import CompressedFileArchive
from timeline.models import Entry

logger = logging.getLogger(__name__)


class RedditArchive(CompressedFileArchive):
    """
    Reads reddit GDPR exports
    """
    def extract_username(self):
        csv_file = self.extracted_files_path / 'statistics.csv'
        for line in csv.DictReader(codecs.iterdecode(csv_file.open('rb'), 'utf-8'), delimiter=',', quotechar='"'):
            if line['statistic'] == 'account name':
                return line['value']

    def extract_entries(self) -> Generator[Entry, None, None]:
        reddit_username = self.extract_username()
        yield from self.extract_comments(reddit_username)
        yield from self.extract_posts(reddit_username)

    def extract_comments(self, reddit_username) -> Generator[Entry, None, None]:
        csv_file = self.extracted_files_path / 'comments.csv'
        for line in csv.DictReader(codecs.iterdecode(csv_file.open('rb'), 'utf-8'), delimiter=',', quotechar='"'):
            yield Entry(
                schema='social.reddit.comment',
                title='',
                description=line['body'],
                source=self.entry_source,
                date_on_timeline=pytz.utc.localize(datetime.strptime(line['date'], '%Y-%m-%d %H:%M:%S UTC')),
                extra_attributes={
                    'post_id': line['id'],
                    'post_body_html': line['body'],
                    'post_parent_id': line['parent'],
                    'post_thread_id': line['permalink'].split('/')[6],
                    'post_community': line['permalink'].split('/')[4],
                    'post_user': reddit_username,
                }
            )

    def extract_posts(self, reddit_username) -> Generator[Entry, None, None]:
        csv_file = self.extracted_files_path / 'posts.csv'
        for line in csv.DictReader(codecs.iterdecode(csv_file.open('rb'), 'utf-8'),
                                   delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL):
            yield Entry(
                schema='social.reddit.post',
                title=line['title'],
                description=line['body'],
                source=self.entry_source,
                date_on_timeline=pytz.utc.localize(datetime.strptime(line['date'], '%Y-%m-%d %H:%M:%S UTC')),
                extra_attributes={
                    'post_id': line['id'],
                    'post_community': line['subreddit'],
                    'post_user': reddit_username,
                    'post_url': line['permalink'],
                }
            )