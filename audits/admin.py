from django.contrib import admin
from audits.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "event_type", "created_at"]
    list_filter = ["event_type", "created_at"]
    search_fields = ["user__username"]
    readonly_fields = ["user", "event_type", "payload", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
