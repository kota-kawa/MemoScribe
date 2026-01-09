from django.contrib import admin
from preferences.models import Preference, UserSettings


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ["key", "category", "user", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["key", "value"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ["user", "send_notes", "send_digests", "pii_masking", "llm_enabled"]
    readonly_fields = ["created_at", "updated_at"]
