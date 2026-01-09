"""
Tasks models for MemoScribe.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Task(models.Model):
    """User task with priority and status."""

    PRIORITY_CHOICES = [
        (1, "低"),
        (2, "普通"),
        (3, "高"),
        (4, "緊急"),
    ]

    STATUS_CHOICES = [
        ("todo", "未着手"),
        ("doing", "進行中"),
        ("done", "完了"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField("タイトル", max_length=255)
    description = models.TextField("説明", blank=True)
    due_at = models.DateTimeField("期限", null=True, blank=True)
    priority = models.IntegerField("優先度", choices=PRIORITY_CHOICES, default=2)
    status = models.CharField("状態", max_length=20, choices=STATUS_CHOICES, default="todo")
    tags = models.JSONField("タグ", default=list, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "タスク"
        verbose_name_plural = "タスク"
        ordering = ["-priority", "due_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tasks:detail", kwargs={"pk": self.pk})

    def get_tags_display(self) -> str:
        """Return tags as comma-separated string."""
        return ", ".join(self.tags) if self.tags else ""

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        from django.utils import timezone
        if self.due_at and self.status != "done":
            return self.due_at < timezone.now()
        return False
