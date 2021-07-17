from django.urls import path, include

urlpatterns = [
    path('archive/', include('archive.urls')),
    path('timeline/', include('timeline.urls')),
    path('source/', include('backup.urls.source')),
    path('destination/', include('backup.urls.destination')),
]
