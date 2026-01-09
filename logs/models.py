"""
Daily logs models for MemoScribe.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class DailyLog(models.Model):
    """Raw daily log entry."""

    MOOD_CHOICES = [
        (1, "😢 とても悪い"),
        (2, "😕 悪い"),
        (3, "😐 普通"),
        (4, "🙂 良い"),
        (5, "😊 とても良い"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_logs")
    date = models.DateField("日付")
    raw_text = models.TextField("内容")
    mood = models.IntegerField("気分", choices=MOOD_CHOICES, null=True, blank=True)
    attachment = models.FileField("添付", upload_to="logs/attachments/", null=True, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "日常ログ"
        verbose_name_plural = "日常ログ"
        ordering = ["-date"]
        unique_together = [["user", "date"]]

    def __str__(self):
        return f"{self.date} - {self.user.username}"

    def get_absolute_url(self):
        return reverse("logs:detail", kwargs={"pk": self.pk})


class DailyDigest(models.Model):
    """Extracted digest from daily log."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_digests")
    log = models.OneToOneField(DailyLog, on_delete=models.CASCADE, related_name="digest")
    summary = models.TextField("要約")
    tags = models.JSONField("タグ", default=list, blank=True)
    topics = models.JSONField("トピック", default=list, blank=True)
    actions = models.JSONField("アクション", default=list, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = "日常ダイジェスト"
        verbose_name_plural = "日常ダイジェスト"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Digest: {self.log.date}"
