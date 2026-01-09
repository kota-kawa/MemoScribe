from django.contrib import admin
from notes.models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "importance", "created_at", "updated_at"]
    list_filter = ["importance", "visibility", "created_at"]
    search_fields = ["title", "body"]
    readonly_fields = ["created_at", "updated_at"]
