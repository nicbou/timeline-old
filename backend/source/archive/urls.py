from django.urls import include, path
from rest_framework import routers
from .views import GoogleTakeoutArchiveViewSet, TwitterArchiveViewSet, JsonArchiveViewSet, GpxArchiveViewSet

router = routers.DefaultRouter()
router.register(r'googletakeoutarchives', GoogleTakeoutArchiveViewSet)
router.register(r'twitterarchives', TwitterArchiveViewSet)
router.register(r'jsonarchives', JsonArchiveViewSet)
router.register(r'gpxarchives', GpxArchiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
