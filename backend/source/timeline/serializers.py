from rest_framework import serializers

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


def serialize_entry(entry: Entry):
    """
    Much faster serializer for entry dumps
    """
    return {
        field: getattr(entry, field)
        for field in EntrySerializer().fields.keys()
    }