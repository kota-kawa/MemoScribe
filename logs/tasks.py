"""
Celery tasks for logs processing.
"""

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_digest(self, log_id: int):
    """Generate digest for a daily log."""
    from logs.models import DailyLog, DailyDigest
    from core.llm import llm_provider
    from retrieval.tasks import update_digest_embedding
    from audits.models import AuditLog
    from core.utils import calculate_token_estimate

    try:
        log = DailyLog.objects.get(pk=log_id)
    except DailyLog.DoesNotExist:
        logger.warning(f"DailyLog {log_id} not found")
        return

    try:
        # Generate digest using LLM
        result = llm_provider.generate_digest(log.raw_text)

        # Create or update digest
        digest, created = DailyDigest.objects.update_or_create(
            log=log,
            defaults={
                "user": log.user,
                "summary": result.get("summary", ""),
                "tags": result.get("tags", []),
                "topics": result.get("topics", []),
                "actions": result.get("actions", []),
            },
        )

        # Log LLM call if LLM was used
        if llm_provider.is_available():
            AuditLog.objects.create(
                user=log.user,
                event_type="llm_call",
                payload={
                    "action": "generate_digest",
                    "log_id": log_id,
                    "tokens": calculate_token_estimate(log.raw_text),
                },
            )

        # Update embedding for the digest
        update_digest_embedding.delay(digest.pk)

        logger.info(f"Generated digest for log {log_id}")

    except Exception as e:
        logger.error(f"Failed to generate digest for log {log_id}: {e}")
        raise self.retry(exc=e, countdown=60)
