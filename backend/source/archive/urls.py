from django.urls import include, path
from rest_framework import routers

from .views import GoogleTakeoutArchiveViewSet, TwitterArchiveViewSet, JsonArchiveViewSet, GpxArchiveViewSet, \
    N26CsvArchiveViewSet, TelegramArchiveViewSet, FacebookArchiveViewSet

router = routers.DefaultRouter()
router.register(r'facebookarchive', FacebookArchiveViewSet)
router.register(r'googletakeoutarchive', GoogleTakeoutArchiveViewSet)
router.register(r'gpxarchive', GpxArchiveViewSet)
router.register(r'jsonarchive', JsonArchiveViewSet)
router.register(r'n26csvarchive', N26CsvArchiveViewSet)
router.register(r'telegramarchive', TelegramArchiveViewSet)
router.register(r'twitterarchive', TwitterArchiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
