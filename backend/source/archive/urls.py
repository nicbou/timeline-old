from django.urls import include, path
from rest_framework import routers
from .views import GoogleTakeoutArchiveViewSet, TwitterArchiveViewSet, JsonArchiveViewSet, GpxArchiveViewSet, \
    N26CsvArchiveViewSet

router = routers.DefaultRouter()
router.register(r'googletakeoutarchives', GoogleTakeoutArchiveViewSet)
router.register(r'twitterarchives', TwitterArchiveViewSet)
router.register(r'jsonarchives', JsonArchiveViewSet)
router.register(r'gpxarchives', GpxArchiveViewSet)
router.register(r'n26csvarchives', N26CsvArchiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
