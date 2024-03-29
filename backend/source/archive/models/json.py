import json
import logging
from typing import Generator

from archive.models.base import FileArchive
from timeline.models import Entry
from timeline.serializers import EntrySerializer

logger = logging.getLogger(__name__)


class JsonArchive(FileArchive):
    """
    A list of JSON entries, as returned by the API
    """
    def extract_entries(self) -> Generator[Entry, None, None]:
        for json_file in self.get_archive_files():
            json_entries = json.load(json_file)
            for json_entry in json_entries:
                json_entry['source'] = self.entry_source
                json_entry.pop('id', None)
                serializer = EntrySerializer(data=json_entry)
                assert serializer.is_valid()
                yield Entry(**serializer.validated_data)
