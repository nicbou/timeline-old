from rest_framework import serializers

from .models import Entry


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = '__all__'


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