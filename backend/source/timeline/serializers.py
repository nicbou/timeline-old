from rest_framework import serializers
from django.apps import apps

from .models import Entry


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Entry
        fields = [
            'id',
            'schema',
            'source',
            'title',
            'description',
            'extra_attributes',
            'date_on_timeline',
        ]


_entry_fields_cache = None


def get_entry_fields():
    global _entry_fields_cache
    if not _entry_fields_cache:
        _entry_fields_cache = EntrySerializer().fields.keys()
    return _entry_fields_cache


def serialize_entry(entry: Entry):
    """
    Much faster serializer for entry dumps
    """
    return {
        field: getattr(entry, field)
        for field in get_entry_fields()
    }