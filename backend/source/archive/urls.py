from django.urls import include, path
from rest_framework import routers
from .views import GoogleTakeoutArchiveViewSet

router = routers.DefaultRouter()
router.register(r'googletakeoutarchive', GoogleTakeoutArchiveViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
