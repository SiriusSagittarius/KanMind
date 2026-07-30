"""
URL configuration for core project.

Central routing: includes the urls.py of each app under /api/.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('kanban_app.api.urls')),
]
