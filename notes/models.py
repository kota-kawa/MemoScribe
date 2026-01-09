"""
Notes models for MemoScribe.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Note(models.Model):
    """User note with markdown support."""

    IMPORTANCE_CHOICES = [
        (1, "低"),
        (2, "普通"),
        (3, "高"),
        (4, "重要"),
        (5, "最重要"),
    ]

    VISIBILITY_CHOICES = [
        ("private", "自分のみ"),
        ("shared", "共有"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField("タイトル", max_length=255)
    body = models.TextField("本文", blank=True)
    tags = models.JSONField("タグ", default=list, blank=True)
    importance = models.IntegerField("重要度", choices=IMPORTANCE_CHOICES, default=2)
    visibility = models.CharField(
        "公開範囲", max_length=20, choices=VISIBILITY_CHOICES, default="private"
    )
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "メモ"
        verbose_name_plural = "メモ"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("notes:detail", kwargs={"pk": self.pk})

    def get_tags_display(self) -> str:
        """Return tags as comma-separated string."""
        return ", ".join(self.tags) if self.tags else ""
