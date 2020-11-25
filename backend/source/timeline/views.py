from .models import Entry
from rest_framework import permissions
from rest_framework import viewsets
from .serializers import EntrySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all().order_by('-date_on_timeline')
    serializer_class = EntrySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    permission_classes = [permissions.AllowAny]
    filterset_fields = {
        'date_on_timeline': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'schema': ['exact', 'contains'],
    }
