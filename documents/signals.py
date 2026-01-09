"""
Documents signals for processing.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from documents.models import Document


@receiver(post_save, sender=Document)
def document_saved(sender, instance, created, **kwargs):
    """Trigger document processing when uploaded."""
    if created:
        from documents.tasks import process_document
        process_document.delay(instance.pk)
