"""
Retrieval service for MemoScribe.
Handles RAG (Retrieval Augmented Generation) operations.
"""

import logging
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import User
from pgvector.django import L2Distance

from retrieval.models import Embedding
from preferences.models import Preference, UserSettings
from core.llm import llm_provider
from core.utils import mask_pii

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving relevant context for RAG."""

    def __init__(self, user: User):
        self.user = user
        self.settings = self._get_user_settings()

    def _get_user_settings(self) -> dict:
        """Get user settings with fallback to environment variables."""
        try:
            user_settings = UserSettings.objects.get(user=self.user)
            return {
                "send_notes": user_settings.send_notes,
                "send_digests": user_settings.send_digests,
                "send_docs": user_settings.send_docs,
                "send_raw_logs": user_settings.send_raw_logs,
                "pii_masking": user_settings.pii_masking,
                "llm_enabled": user_settings.llm_enabled,
            }
        except UserSettings.DoesNotExist:
            return {
                "send_notes": settings.SEND_NOTES,
                "send_digests": settings.SEND_DIGESTS,
                "send_docs": settings.SEND_DOCS,
                "send_raw_logs": settings.SEND_RAW_LOGS,
                "pii_masking": settings.PII_MASKING,
                "llm_enabled": settings.LLM_ENABLED,
            }

    def _get_allowed_content_types(self) -> list[str]:
        """Get list of content types allowed to be sent to LLM."""
        allowed = []
        if self.settings["send_notes"]:
            allowed.append("note")
        if self.settings["send_digests"]:
            allowed.append("digest")
        if self.settings["send_docs"]:
            allowed.append("chunk")
        # Tasks and preferences are always allowed
        allowed.extend(["task", "preference"])
        return allowed

    def retrieve(self, query: str, top_k: int = 8) -> list[dict]:
        """
        Retrieve relevant context items for a query.

        Args:
            query: User's query text
            top_k: Number of results to return

        Returns:
            List of context items with id, type, title, content
        """
        if not llm_provider.is_available():
            # Fall back to keyword search
            return self._keyword_search(query, top_k)

        # Generate query embedding
        query_vector = llm_provider.generate_embedding(query)
        if not query_vector:
            return self._keyword_search(query, top_k)

        # Get allowed content types
        allowed_types = self._get_allowed_content_types()

        # Vector similarity search
        results = (
            Embedding.objects.filter(
                user=self.user,
                content_type__in=allowed_types,
                vector__isnull=False,
            )
            .annotate(distance=L2Distance("vector", query_vector))
            .order_by("distance")[:top_k]
        )

        context_items = []
        for r in results:
            content = r.content_text
            if self.settings["pii_masking"]:
                content = mask_pii(content)

            context_items.append({
                "id": r.content_id,
                "type": r.content_type,
                "title": r.content_title,
                "content": content[:500],  # Limit content length
            })

        return context_items

    def _keyword_search(self, query: str, limit: int) -> list[dict]:
        """Fallback keyword search when vector search unavailable."""
        from django.db.models import Q
        from notes.models import Note
        from logs.models import DailyDigest
        from documents.models import DocumentChunk
        from tasks.models import Task

        results = []

        # Search notes
        if self.settings["send_notes"]:
            notes = Note.objects.filter(
                user=self.user
            ).filter(
                Q(title__icontains=query) | Q(body__icontains=query)
            )[:limit // 4]
            for note in notes:
                content = f"{note.title}\n{note.body}"
                if self.settings["pii_masking"]:
                    content = mask_pii(content)
                results.append({
                    "id": note.pk,
                    "type": "note",
                    "title": note.title,
                    "content": content[:500],
                })

        # Search digests
        if self.settings["send_digests"]:
            digests = DailyDigest.objects.filter(
                user=self.user,
                summary__icontains=query,
            )[:limit // 4]
            for digest in digests:
                content = digest.summary
                if self.settings["pii_masking"]:
                    content = mask_pii(content)
                results.append({
                    "id": digest.pk,
                    "type": "digest",
                    "title": f"ダイジェスト: {digest.log.date}",
                    "content": content[:500],
                })

        # Search document chunks
        if self.settings["send_docs"]:
            chunks = DocumentChunk.objects.filter(
                document__user=self.user,
                content__icontains=query,
            )[:limit // 4]
            for chunk in chunks:
                content = chunk.content
                if self.settings["pii_masking"]:
                    content = mask_pii(content)
                results.append({
                    "id": chunk.pk,
                    "type": "chunk",
                    "title": f"{chunk.document.title} - Chunk {chunk.chunk_index}",
                    "content": content[:500],
                })

        # Search tasks
        tasks = Task.objects.filter(
            user=self.user
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:limit // 4]
        for task in tasks:
            content = f"{task.title}\n{task.description}"
            if self.settings["pii_masking"]:
                content = mask_pii(content)
            results.append({
                "id": task.pk,
                "type": "task",
                "title": task.title,
                "content": content[:500],
            })

        return results[:limit]

    def get_user_preferences(self) -> list[dict]:
        """Get user preferences for LLM context."""
        prefs = Preference.objects.filter(user=self.user)
        return [{"key": p.key, "value": p.value} for p in prefs]
