from django.urls import include, path
from rest_framework import routers
from .views import GoogleTakeoutArchiveViewSet, TwitterArchiveViewSet

router = routers.DefaultRouter()
router.register(r'googletakeoutarchives', GoogleTakeoutArchiveViewSet)
router.register(r'twitterarchives', TwitterArchiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
