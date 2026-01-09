"""
Audit log models for MemoScribe.
"""

from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    """Audit log for tracking important events."""

    EVENT_TYPES = [
        ("llm_call", "LLM呼び出し"),
        ("data_export", "データエクスポート"),
        ("data_delete", "データ削除"),
        ("login", "ログイン"),
        ("logout", "ログアウト"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="audit_logs")
    event_type = models.CharField("イベント種類", max_length=50, choices=EVENT_TYPES)
    payload = models.JSONField("ペイロード", default=dict, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = "監査ログ"
        verbose_name_plural = "監査ログ"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.event_type} - {self.created_at}"
