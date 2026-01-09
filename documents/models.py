"""
Documents models for MemoScribe.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Document(models.Model):
    """Uploaded document with extracted text."""

    STATUS_CHOICES = [
        ("pending", "処理待ち"),
        ("processing", "処理中"),
        ("completed", "完了"),
        ("failed", "失敗"),
    ]

    FILE_TYPE_CHOICES = [
        ("pdf", "PDF"),
        ("txt", "テキスト"),
        ("md", "Markdown"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField("タイトル", max_length=255)
    file = models.FileField("ファイル", upload_to="documents/files/")
    file_type = models.CharField("ファイル形式", max_length=10, choices=FILE_TYPE_CHOICES)
    extracted_text = models.TextField("抽出テキスト", blank=True)
    summary = models.TextField("要約", blank=True)
    status = models.CharField("状態", max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField("エラーメッセージ", blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "文書"
        verbose_name_plural = "文書"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("documents:detail", kwargs={"pk": self.pk})


class DocumentChunk(models.Model):
    """Chunk of document text for RAG."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.IntegerField("チャンク番号")
    content = models.TextField("内容")
    metadata = models.JSONField("メタデータ", default=dict, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = "文書チャンク"
        verbose_name_plural = "文書チャンク"
        ordering = ["document", "chunk_index"]
        unique_together = [["document", "chunk_index"]]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
