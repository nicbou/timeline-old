from .models import Entry
from rest_framework import serializers


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Entry
        fields = [
            'schema', 
            'title', 
            'description', 
            'extra_attributes',
            'date_on_timeline',
        ]
