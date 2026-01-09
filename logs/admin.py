from django.contrib import admin
from logs.models import DailyLog, DailyDigest


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ["date", "user", "mood", "created_at"]
    list_filter = ["mood", "date"]
    search_fields = ["raw_text"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DailyDigest)
class DailyDigestAdmin(admin.ModelAdmin):
    list_display = ["log", "user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["summary"]
    readonly_fields = ["created_at"]
