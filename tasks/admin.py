from django.contrib import admin
from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "priority", "status", "due_at", "created_at"]
    list_filter = ["status", "priority", "created_at"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
