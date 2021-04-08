from django.urls import include, path
from rest_framework import routers
from .views import RsyncSourceViewSet, RsyncDestinationViewSet, TwitterSourceViewSet, RedditSourceViewSet, \
    HackerNewsSourceViewSet, RssSourceViewSet, FileSystemSourceViewSet

router = routers.DefaultRouter()
router.register(r'rsyncsource', RsyncSourceViewSet)
router.register(r'rsyncdestination', RsyncDestinationViewSet)
router.register(r'twittersource', TwitterSourceViewSet)
router.register(r'redditsource', RedditSourceViewSet)
router.register(r'hackernewssource', HackerNewsSourceViewSet)
router.register(r'rsssource', RssSourceViewSet)
router.register(r'filesystemsource', FileSystemSourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
