"""
Logs signals for digest generation.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from logs.models import DailyLog


@receiver(post_save, sender=DailyLog)
def log_saved(sender, instance, created, **kwargs):
    """Trigger digest generation when log is saved."""
    from logs.tasks import generate_digest
    generate_digest.delay(instance.pk)
