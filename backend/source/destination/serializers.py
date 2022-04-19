from rest_framework import serializers

from destination.models.rsync import RsyncDestination


class BaseDestinationSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()


class RsyncDestinationSerializer(BaseDestinationSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = RsyncDestination
        fields = '__all__'
