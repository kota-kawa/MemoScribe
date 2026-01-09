"""
Assistant URL configuration.
"""

from django.urls import path
from assistant import views

app_name = "assistant"

urlpatterns = [
    path("", views.session_list, name="list"),
    path("new/", views.session_create, name="create"),
    path("<int:pk>/", views.session_detail, name="session"),
    path("<int:pk>/send/", views.send_message, name="send"),
    path("<int:pk>/write/", views.generate_writing, name="write"),
    path("<int:pk>/delete/", views.session_delete, name="delete"),
]
