"""
URL configuration for MemoScribe project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from core.views import home, dashboard, settings_view, search_view, signup

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication
    path("signup/", signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Core
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("settings/", settings_view, name="settings"),
    path("search/", search_view, name="search"),
    # Apps
    path("notes/", include("notes.urls")),
    path("logs/", include("logs.urls")),
    path("documents/", include("documents.urls")),
    path("tasks/", include("tasks.urls")),
    path("preferences/", include("preferences.urls")),
    path("assistant/", include("assistant.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
