from django.contrib import admin
from assistant.models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "created_at", "updated_at"]
    list_filter = ["created_at"]
    search_fields = ["title", "user__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["session", "role", "created_at"]
    list_filter = ["role", "created_at"]
    search_fields = ["content"]
    readonly_fields = ["created_at"]
