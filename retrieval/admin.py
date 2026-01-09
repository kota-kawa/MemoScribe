from django.contrib import admin
from retrieval.models import Embedding


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ["content_type", "content_id", "content_title", "user", "created_at"]
    list_filter = ["content_type", "created_at"]
    search_fields = ["content_title", "content_text"]
    readonly_fields = ["created_at", "updated_at"]
