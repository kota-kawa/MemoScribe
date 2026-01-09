"""
Celery tasks for embedding generation.
"""

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


def generate_and_store_embedding(content_type: str, content_id: int, user_id: int, title: str, text: str):
    """Generate embedding and store in database."""
    from retrieval.models import Embedding
    from core.llm import llm_provider
    from django.contrib.auth.models import User

    if not text:
        logger.warning(f"Empty text for {content_type}:{content_id}")
        return

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning(f"User {user_id} not found")
        return

    # Generate embedding vector
    vector = llm_provider.generate_embedding(text[:8000])

    # Create or update embedding record
    Embedding.objects.update_or_create(
        content_type=content_type,
        content_id=content_id,
        defaults={
            "user": user,
            "content_text": text[:10000],  # Store truncated text
            "content_title": title[:255],
            "vector": vector,
        },
    )

    logger.info(f"Updated embedding for {content_type}:{content_id}")


@shared_task(bind=True, max_retries=3)
def update_note_embedding(self, note_id: int):
    """Update embedding for a note."""
    from notes.models import Note

    try:
        note = Note.objects.get(pk=note_id)
        text = f"{note.title}\n\n{note.body}"
        generate_and_store_embedding("note", note_id, note.user_id, note.title, text)
    except Note.DoesNotExist:
        logger.warning(f"Note {note_id} not found")
    except Exception as e:
        logger.error(f"Failed to update note embedding: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def delete_note_embedding(note_id: int):
    """Delete embedding for a note."""
    from retrieval.models import Embedding
    Embedding.objects.filter(content_type="note", content_id=note_id).delete()


@shared_task(bind=True, max_retries=3)
def update_digest_embedding(self, digest_id: int):
    """Update embedding for a digest."""
    from logs.models import DailyDigest

    try:
        digest = DailyDigest.objects.get(pk=digest_id)
        text = f"{digest.summary}\n\nトピック: {', '.join(digest.topics)}\nアクション: {', '.join(digest.actions)}"
        title = f"ダイジェスト: {digest.log.date}"
        generate_and_store_embedding("digest", digest_id, digest.user_id, title, text)
    except DailyDigest.DoesNotExist:
        logger.warning(f"Digest {digest_id} not found")
    except Exception as e:
        logger.error(f"Failed to update digest embedding: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def update_chunk_embedding(self, chunk_id: int):
    """Update embedding for a document chunk."""
    from documents.models import DocumentChunk

    try:
        chunk = DocumentChunk.objects.select_related("document").get(pk=chunk_id)
        title = f"{chunk.document.title} - Chunk {chunk.chunk_index}"
        generate_and_store_embedding("chunk", chunk_id, chunk.document.user_id, title, chunk.content)
    except DocumentChunk.DoesNotExist:
        logger.warning(f"Chunk {chunk_id} not found")
    except Exception as e:
        logger.error(f"Failed to update chunk embedding: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def update_task_embedding(self, task_id: int):
    """Update embedding for a task."""
    from tasks.models import Task

    try:
        task = Task.objects.get(pk=task_id)
        text = f"{task.title}\n\n{task.description}"
        generate_and_store_embedding("task", task_id, task.user_id, task.title, text)
    except Task.DoesNotExist:
        logger.warning(f"Task {task_id} not found")
    except Exception as e:
        logger.error(f"Failed to update task embedding: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def delete_task_embedding(task_id: int):
    """Delete embedding for a task."""
    from retrieval.models import Embedding
    Embedding.objects.filter(content_type="task", content_id=task_id).delete()


@shared_task(bind=True, max_retries=3)
def update_preference_embedding(self, pref_id: int):
    """Update embedding for a preference."""
    from preferences.models import Preference

    try:
        pref = Preference.objects.get(pk=pref_id)
        text = f"{pref.key}: {pref.value}"
        generate_and_store_embedding("preference", pref_id, pref.user_id, pref.key, text)
    except Preference.DoesNotExist:
        logger.warning(f"Preference {pref_id} not found")
    except Exception as e:
        logger.error(f"Failed to update preference embedding: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def delete_preference_embedding(pref_id: int):
    """Delete embedding for a preference."""
    from retrieval.models import Embedding
    Embedding.objects.filter(content_type="preference", content_id=pref_id).delete()
