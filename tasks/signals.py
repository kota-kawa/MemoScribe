"""
Tasks signals for embedding updates.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from tasks.models import Task


@receiver(post_save, sender=Task)
def task_saved(sender, instance, created, **kwargs):
    """Trigger embedding update when task is saved."""
    from retrieval.tasks import update_task_embedding
    update_task_embedding.delay(instance.pk)


@receiver(post_delete, sender=Task)
def task_deleted(sender, instance, **kwargs):
    """Clean up embeddings when task is deleted."""
    from retrieval.tasks import delete_task_embedding
    delete_task_embedding.delay(instance.pk)
