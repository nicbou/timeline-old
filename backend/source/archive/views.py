from rest_framework import viewsets, permissions

from archive.models.google_takeout import GoogleTakeoutArchive
from archive.serializers import GoogleTakeoutArchiveSerializer


class GoogleTakeoutArchiveViewSet(viewsets.ModelViewSet):
    queryset = GoogleTakeoutArchive.objects.all()
    serializer_class = GoogleTakeoutArchiveSerializer
    permission_classes = [permissions.AllowAny]
