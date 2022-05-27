from oauth2_provider.contrib.rest_framework import TokenMatchesOASRequirements

from source.views import RsyncSourceViewSet
from destination.models import RsyncDestination
from destination.serializers import RsyncDestinationSerializer


class RsyncDestinationViewSet(RsyncSourceViewSet):
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["destination:read"]],
        "POST": [["destination:write"]],
        "PUT":  [["destination:write"]],
        "DELETE": [["destination:write"]],
    }

    queryset = RsyncDestination.objects.all().order_by('key')
    serializer_class = RsyncDestinationSerializer
