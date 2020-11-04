from django.urls import include, path
from rest_framework import routers
from .views import BackupSourceViewSet, BackupViewSet, TwitterSourceViewSet, RedditSourceViewSet

router = routers.DefaultRouter()
router.register(r'backupsources', BackupSourceViewSet)
router.register(r'twittersources', TwitterSourceViewSet)
router.register(r'redditsources', RedditSourceViewSet)
router.register(r'backups', BackupViewSet, basename='backups')

urlpatterns = [
    path('', include(router.urls)),
]