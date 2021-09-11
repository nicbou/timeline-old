from django.urls import include, path
from rest_framework import routers

from .views import GoogleTakeoutArchiveViewSet, TwitterArchiveViewSet, JsonArchiveViewSet, GpxArchiveViewSet, \
    N26CsvArchiveViewSet, TelegramArchiveViewSet, FacebookArchiveViewSet, ArchiveFileViewSet

router = routers.DefaultRouter()
router.register(r'facebook', FacebookArchiveViewSet)
router.register(r'googletakeout', GoogleTakeoutArchiveViewSet)
router.register(r'gpx', GpxArchiveViewSet)
router.register(r'json', JsonArchiveViewSet)
router.register(r'n26csv', N26CsvArchiveViewSet)
router.register(r'telegram', TelegramArchiveViewSet)
router.register(r'twitter', TwitterArchiveViewSet)
router.register(r'archivefile', ArchiveFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
