from django.urls import include, path
from rest_framework import routers

from .views import RsyncSourceViewSet, RsyncDestinationViewSet, TwitterSourceViewSet, RedditSourceViewSet, \
    HackerNewsSourceViewSet, RssSourceViewSet, FileSystemSourceViewSet

router = routers.DefaultRouter()
router.register(r'destination/rsync', RsyncDestinationViewSet)
router.register(r'source/filesystem', FileSystemSourceViewSet)
router.register(r'source/hackernews', HackerNewsSourceViewSet)
router.register(r'source/reddit', RedditSourceViewSet)
router.register(r'source/rss', RssSourceViewSet)
router.register(r'source/rsync', RsyncSourceViewSet)
router.register(r'source/twitter', TwitterSourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
