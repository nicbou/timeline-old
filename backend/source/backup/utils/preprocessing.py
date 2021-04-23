import logging

from django.conf import settings
from rest_framework.renderers import JSONRenderer

from timeline.models import Entry
from timeline.serializers import EntrySerializer

logger = logging.getLogger(__name__)


def dump_entries():
    logger.info(f"Dumping all entries in {settings.ENTRIES_DUMP_PATH}")
    with settings.ENTRIES_DUMP_PATH.open('w+') as entry_dump:
        entry_dump.write('[')
        entries = Entry.objects.iterator(chunk_size=5000)
        for index, entry in enumerate(entries):
            if index > 0:
                entry_dump.write(',')
            entry_dump.write(JSONRenderer().render(EntrySerializer(entry).data).decode("utf-8"))
        entry_dump.write(']')