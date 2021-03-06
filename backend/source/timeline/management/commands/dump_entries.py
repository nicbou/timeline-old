import logging

from django.core.management.base import BaseCommand
from rest_framework.renderers import JSONRenderer

from timeline.models import Entry
from timeline.serializers import EntrySerializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Exports all entries as JSON'

    def handle(self, *args, **options):
        print('[', end='')
        entries = Entry.objects.iterator(chunk_size=5000)
        for index, entry in enumerate(entries):
            if index > 0:
                print(',', end='')
            print(JSONRenderer().render(EntrySerializer(entry).data).decode("utf-8"), end='')
        print(']', end='')
