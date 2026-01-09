"""
Preferences models for MemoScribe.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Preference(models.Model):
    """User preference, rule, or policy."""

    CATEGORY_CHOICES = [
        ("writing", "文章スタイル"),
        ("lifestyle", "生活習慣"),
        ("work", "仕事"),
        ("health", "健康"),
        ("decision", "意思決定"),
        ("other", "その他"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="preferences")
    key = models.CharField("キー", max_length=255)
    value = models.TextField("値")
    category = models.CharField("カテゴリ", max_length=50, choices=CATEGORY_CHOICES, default="other")
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "好み・ルール"
        verbose_name_plural = "好み・ルール"
        ordering = ["category", "key"]
        unique_together = [["user", "key"]]

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

    def get_absolute_url(self):
        return reverse("preferences:edit", kwargs={"pk": self.pk})


class UserSettings(models.Model):
    """User-specific settings that override environment variables."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    send_notes = models.BooleanField("メモを送信", default=True)
    send_digests = models.BooleanField("ダイジェストを送信", default=True)
    send_docs = models.BooleanField("文書を送信", default=False)
    send_raw_logs = models.BooleanField("生ログを送信", default=False)
    pii_masking = models.BooleanField("PII マスキング", default=True)
    llm_enabled = models.BooleanField("LLM 有効", default=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "ユーザー設定"
        verbose_name_plural = "ユーザー設定"

    def __str__(self):
        return f"Settings: {self.user.username}"
