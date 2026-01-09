"""
Assistant models for MemoScribe chat.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class ChatSession(models.Model):
    """Chat session with the assistant."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField("タイトル", max_length=255, default="新しい会話")
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "チャットセッション"
        verbose_name_plural = "チャットセッション"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def get_absolute_url(self):
        return reverse("assistant:session", kwargs={"pk": self.pk})


class ChatMessage(models.Model):
    """Individual message in a chat session."""

    ROLE_CHOICES = [
        ("user", "ユーザー"),
        ("assistant", "アシスタント"),
        ("system", "システム"),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField("役割", max_length=20, choices=ROLE_CHOICES)
    content = models.TextField("内容")
    citations = models.JSONField("引用", default=list, blank=True)
    next_questions = models.JSONField("追加質問", default=list, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = "チャットメッセージ"
        verbose_name_plural = "チャットメッセージ"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
