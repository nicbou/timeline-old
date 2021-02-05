import json
import logging
from datetime import datetime
from typing import Tuple

import pytz
from django.db import transaction

from archive.models.base import BaseArchive
from timeline.models import Entry
from timeline.serializers import EntrySerializer

logger = logging.getLogger(__name__)


class JsonArchive(BaseArchive):
    """
    A list of JSON entries, as returned by the API
    """
    source_name = 'json'

    def process(self) -> Tuple[int, int]:
        total_entries_created = 0
        try:
            with transaction.atomic():
                self.delete_entries()
                json_entries = json.load(self.archive_file.file)
                for json_entry in json_entries:
                    json_entry['source'] = self.entry_source
                    serializer = EntrySerializer(data=json_entry)
                    serializer.is_valid()
                    serializer.save()
                    total_entries_created += 1

                self.date_processed = datetime.now(pytz.UTC)
                self.save()
        except:
            logger.exception(f'Failed to process archive "{self.key}"')
            raise
        finally:
            self.delete_extracted_files()

        logging.info(f'Done processing "{self.key}" archive. {total_entries_created} entries created.')
        return total_entries_created, 0
