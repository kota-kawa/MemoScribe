"""
Tasks URL configuration.
"""

from django.urls import path
from tasks import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_list, name="list"),
    path("new/", views.task_create, name="create"),
    path("<int:pk>/", views.task_detail, name="detail"),
    path("<int:pk>/edit/", views.task_edit, name="edit"),
    path("<int:pk>/delete/", views.task_delete, name="delete"),
    path("<int:pk>/toggle/", views.task_toggle_status, name="toggle"),
]
