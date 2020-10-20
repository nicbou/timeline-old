from .models import BackupSource
from rest_framework import permissions
from rest_framework import viewsets
from .serializers import BackupSourceSerializer
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


class BackupSourceViewSet(viewsets.ModelViewSet):
    queryset = BackupSource.objects.all().order_by('host')
    serializer_class = BackupSourceSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        data = serializer.validated_data
        call_command(
            'copy_ssh_keys',
            user=data.get('user'),
            password=data.pop('password'),
            host=data.get('host'),
            port=data.get('port'),
        )
        
        return super().perform_create(serializer)
