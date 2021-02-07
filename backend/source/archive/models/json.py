import json
import logging
from typing import Generator

from archive.models.base import BaseArchive
from timeline.models import Entry
from timeline.serializers import EntrySerializer

logger = logging.getLogger(__name__)


class JsonArchive(BaseArchive):
    """
    A list of JSON entries, as returned by the API
    """
    source_name = 'json'

    def extract_entries(self) -> Generator[Entry, None, None]:
        json_entries = json.load(self.archive_file.file)
        for json_entry in json_entries:
            json_entry['source'] = self.entry_source
            serializer = EntrySerializer(data=json_entry)
            assert serializer.is_valid()
            yield Entry(**serializer.validated_data)
