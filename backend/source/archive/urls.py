from django.urls import include, path
from rest_framework import routers

from .views import GoogleTakeoutArchiveViewSet, TwitterArchiveViewSet, JsonArchiveViewSet, GpxArchiveViewSet, \
    N26CsvArchiveViewSet

router = routers.DefaultRouter()
router.register(r'googletakeoutarchive', GoogleTakeoutArchiveViewSet)
router.register(r'twitterarchive', TwitterArchiveViewSet)
router.register(r'jsonarchive', JsonArchiveViewSet)
router.register(r'gpxarchive', GpxArchiveViewSet)
router.register(r'n26csvarchive', N26CsvArchiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
