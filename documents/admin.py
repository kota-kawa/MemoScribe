from django.contrib import admin
from documents.models import Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "file_type", "status", "created_at"]
    list_filter = ["status", "file_type", "created_at"]
    search_fields = ["title", "extracted_text"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ["document", "chunk_index", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["content"]
