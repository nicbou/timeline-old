from django.urls import include, path
from rest_framework import routers

from source.views import FileSystemSourceViewSet, HackerNewsSourceViewSet, RedditSourceViewSet, RssSourceViewSet, \
    RsyncSourceViewSet, TwitterSourceViewSet, GitSourceViewSet

router = routers.DefaultRouter()
router.register(r'filesystem', FileSystemSourceViewSet)
router.register(r'git', GitSourceViewSet)
router.register(r'hackernews', HackerNewsSourceViewSet)
router.register(r'reddit', RedditSourceViewSet)
router.register(r'rss', RssSourceViewSet)
router.register(r'rsync', RsyncSourceViewSet)
router.register(r'twitter', TwitterSourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
