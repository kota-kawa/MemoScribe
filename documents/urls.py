"""
Documents URL configuration.
"""

from django.urls import path
from documents import views

app_name = "documents"

urlpatterns = [
    path("", views.document_list, name="list"),
    path("new/", views.document_create, name="create"),
    path("<int:pk>/", views.document_detail, name="detail"),
    path("<int:pk>/delete/", views.document_delete, name="delete"),
]
