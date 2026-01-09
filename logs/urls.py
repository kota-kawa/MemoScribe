"""
Logs URL configuration.
"""

from django.urls import path
from logs import views

app_name = "logs"

urlpatterns = [
    path("", views.log_list, name="list"),
    path("new/", views.log_create, name="create"),
    path("<int:pk>/", views.log_detail, name="detail"),
    path("<int:pk>/edit/", views.log_edit, name="edit"),
    path("<int:pk>/delete/", views.log_delete, name="delete"),
    path("<int:pk>/digest/", views.log_digest, name="digest"),
]
