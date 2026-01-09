"""
Preferences signals for embedding updates.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from preferences.models import Preference


@receiver(post_save, sender=Preference)
def preference_saved(sender, instance, created, **kwargs):
    """Trigger embedding update when preference is saved."""
    from retrieval.tasks import update_preference_embedding
    update_preference_embedding.delay(instance.pk)


@receiver(post_delete, sender=Preference)
def preference_deleted(sender, instance, **kwargs):
    """Clean up embeddings when preference is deleted."""
    from retrieval.tasks import delete_preference_embedding
    delete_preference_embedding.delay(instance.pk)
