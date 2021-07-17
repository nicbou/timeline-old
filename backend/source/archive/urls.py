from django.urls import include, path
from rest_framework import routers

from .views import GoogleTakeoutArchiveViewSet, TwitterArchiveViewSet, JsonArchiveViewSet, GpxArchiveViewSet, \
    N26CsvArchiveViewSet, TelegramArchiveViewSet, FacebookArchiveViewSet

router = routers.DefaultRouter()
router.register(r'archive/facebook', FacebookArchiveViewSet)
router.register(r'archive/googletakeout', GoogleTakeoutArchiveViewSet)
router.register(r'archive/gpx', GpxArchiveViewSet)
router.register(r'archive/json', JsonArchiveViewSet)
router.register(r'archive/n26csv', N26CsvArchiveViewSet)
router.register(r'archive/telegram', TelegramArchiveViewSet)
router.register(r'archive/twitter', TwitterArchiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
