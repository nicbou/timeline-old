from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('archive/', include('archive.urls')),
    path('auth/', include('authentication.urls')),
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('timeline/', include('timeline.urls')),
    path('source/', include('source.urls')),
    path('destination/', include('destination.urls')),
]
