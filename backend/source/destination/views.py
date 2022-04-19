from backup.views import RsyncSourceViewSet
from destination.models import RsyncDestination
from destination.serializers import RsyncDestinationSerializer


class RsyncDestinationViewSet(RsyncSourceViewSet):
    queryset = RsyncDestination.objects.all().order_by('key')
    serializer_class = RsyncDestinationSerializer
