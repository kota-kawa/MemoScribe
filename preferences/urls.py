"""
Preferences URL configuration.
"""

from django.urls import path
from preferences import views

app_name = "preferences"

urlpatterns = [
    path("", views.preference_list, name="list"),
    path("new/", views.preference_create, name="create"),
    path("<int:pk>/edit/", views.preference_edit, name="edit"),
    path("<int:pk>/delete/", views.preference_delete, name="delete"),
]
