from .models import Entry
from rest_framework import serializers


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Entry
        fields = [
            'id',
            'schema', 
            'title', 
            'description', 
            'extra_attributes',
            'date_on_timeline',
        ]
