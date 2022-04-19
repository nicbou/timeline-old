from django.urls import path, include

urlpatterns = [
    path('archive/', include('archive.urls')),
    path('timeline/', include('timeline.urls')),
    path('source/', include('source.urls')),
    path('destination/', include('destination.urls')),
]
