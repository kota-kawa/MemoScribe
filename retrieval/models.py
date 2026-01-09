"""
Retrieval models for MemoScribe.
Stores embeddings using pgvector.
"""

from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField


class Embedding(models.Model):
    """Generic embedding storage for any content type."""

    CONTENT_TYPES = [
        ("note", "メモ"),
        ("digest", "ダイジェスト"),
        ("chunk", "文書チャンク"),
        ("task", "タスク"),
        ("preference", "好み"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="embeddings")
    content_type = models.CharField("コンテンツ種類", max_length=20, choices=CONTENT_TYPES)
    content_id = models.IntegerField("コンテンツID")
    content_text = models.TextField("コンテンツテキスト")
    content_title = models.CharField("タイトル", max_length=255, blank=True)
    vector = VectorField(dimensions=1536, null=True, blank=True)  # text-embedding-3-small
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "埋め込み"
        verbose_name_plural = "埋め込み"
        unique_together = [["content_type", "content_id"]]
        indexes = [
            models.Index(fields=["user", "content_type"]),
        ]

    def __str__(self):
        return f"{self.content_type}:{self.content_id}"
