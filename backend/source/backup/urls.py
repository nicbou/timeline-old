from django.urls import include, path
from rest_framework import routers
from .views import RsyncSourceViewSet, BackupViewSet, TwitterSourceViewSet, RedditSourceViewSet, \
    HackerNewsSourceViewSet, RssSourceViewSet, FileSystemSourceViewSet

router = routers.DefaultRouter()
router.register(r'rsyncsources', RsyncSourceViewSet)
router.register(r'twittersources', TwitterSourceViewSet)
router.register(r'redditsources', RedditSourceViewSet)
router.register(r'hackernewssources', HackerNewsSourceViewSet)
router.register(r'rsssources', RssSourceViewSet)
router.register(r'filesystemsources', FileSystemSourceViewSet)
router.register(r'backups', BackupViewSet, basename='backups')

urlpatterns = [
    path('', include(router.urls)),
]
