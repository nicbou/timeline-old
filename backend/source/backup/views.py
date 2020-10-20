from .models import BackupSource
from rest_framework import permissions
from rest_framework import viewsets
from .serializers import BackupSourceSerializer


class BackupSourceViewSet(viewsets.ModelViewSet):
    queryset = BackupSource.objects.all().order_by('host')
    serializer_class = BackupSourceSerializer
    permission_classes = [permissions.AllowAny]