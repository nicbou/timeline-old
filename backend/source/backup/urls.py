from django.urls import include, path
from rest_framework import routers
from .views import BackupSourceViewSet

router = routers.DefaultRouter()
router.register(r'sources', BackupSourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]