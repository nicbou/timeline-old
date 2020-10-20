from .models import Entry
from rest_framework import permissions
from rest_framework import viewsets
from .serializers import EntrySerializer


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all().order_by('-date_on_timeline')
    serializer_class = EntrySerializer
    permission_classes = [permissions.AllowAny]