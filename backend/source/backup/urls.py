from django.urls import include, path
from rest_framework import routers
from .views import BackupSourceViewSet, BackupViewSet

router = routers.DefaultRouter()
router.register(r'sources', BackupSourceViewSet)
router.register(r'backups', BackupViewSet, basename='backups')

urlpatterns = [
    path('', include(router.urls)),
]