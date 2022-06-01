from destination.models import RsyncDestination
from destination.serializers import RsyncDestinationSerializer
from source.views import RsyncSourceViewSet


class RsyncDestinationViewSet(RsyncSourceViewSet):
    required_alternate_scopes = {
        "GET": [["destination:read"]],
        "POST": [["destination:write"]],
        "PUT":  [["destination:write"]],
        "DELETE": [["destination:write"]],
    }

    queryset = RsyncDestination.objects.all().order_by('key')
    serializer_class = RsyncDestinationSerializer
