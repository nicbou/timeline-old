from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('archive/', include('archive.urls')),
    path('timeline/', include('timeline.urls')),
    path('backup/', include('backup.urls')),
]
