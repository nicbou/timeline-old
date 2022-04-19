from django.urls import include, path
from rest_framework import routers

from destination.views import RsyncDestinationViewSet

router = routers.DefaultRouter()
router.register(r'rsync', RsyncDestinationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
