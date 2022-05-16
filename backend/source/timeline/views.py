import json

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from .models import Entry
from .serializers import EntrySerializer


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all().order_by('date_on_timeline')
    serializer_class = EntrySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'date_on_timeline': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'schema': ['exact', 'contains'],
        'source': ['exact', 'contains'],
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return HttpResponse(json.dumps(serializer.data, ensure_ascii=False), content_type="application/json")