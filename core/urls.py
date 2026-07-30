"""
URL configuration for core project.

Zentrales Routing: bindet die urls.py der einzelnen Apps unter /api/ ein.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('kanban_app.api.urls')),
]
