from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('archive.urls')),
    path('', include('timeline.urls')),
    path('', include('backup.urls')),
]
