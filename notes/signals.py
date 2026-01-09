"""
Notes signals for embedding updates.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from notes.models import Note


@receiver(post_save, sender=Note)
def note_saved(sender, instance, created, **kwargs):
    """Trigger embedding update when note is saved."""
    from retrieval.tasks import update_note_embedding
    update_note_embedding.delay(instance.pk)


@receiver(post_delete, sender=Note)
def note_deleted(sender, instance, **kwargs):
    """Clean up embeddings when note is deleted."""
    from retrieval.tasks import delete_note_embedding
    delete_note_embedding.delay(instance.pk)
