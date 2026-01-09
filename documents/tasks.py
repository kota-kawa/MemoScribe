"""
Celery tasks for document processing.
"""

import io
import logging
from celery import shared_task

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 100  # Overlap between chunks


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using pdfminer."""
    from pdfminer.high_level import extract_text
    try:
        return extract_text(file_path)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract text based on file type."""
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    else:
        # Plain text or markdown
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence or paragraph
        if end < len(text):
            # Look for natural break points
            for sep in ["\n\n", "。", ".", "\n", " "]:
                last_sep = chunk.rfind(sep)
                if last_sep > chunk_size // 2:
                    chunk = chunk[:last_sep + len(sep)]
                    end = start + len(chunk)
                    break

        chunks.append(chunk.strip())
        start = end - overlap

    return [c for c in chunks if c]


@shared_task(bind=True, max_retries=3)
def process_document(self, document_id: int):
    """Process an uploaded document: extract text, chunk, summarize, and embed."""
    from documents.models import Document, DocumentChunk
    from core.llm import llm_provider
    from retrieval.tasks import update_chunk_embedding
    from audits.models import AuditLog
    from core.utils import calculate_token_estimate

    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        logger.warning(f"Document {document_id} not found")
        return

    try:
        doc.status = "processing"
        doc.save()

        # Extract text
        file_path = doc.file.path
        extracted_text = extract_text_from_file(file_path, doc.file_type)
        doc.extracted_text = extracted_text

        # Generate summary
        if llm_provider.is_available() and extracted_text:
            digest = llm_provider.generate_digest(extracted_text[:4000])
            doc.summary = digest.get("summary", "")

            # Log LLM call
            AuditLog.objects.create(
                user=doc.user,
                event_type="llm_call",
                payload={
                    "action": "document_summary",
                    "document_id": document_id,
                    "tokens": calculate_token_estimate(extracted_text[:4000]),
                },
            )
        else:
            # Simple summary
            from core.utils import simple_summary
            doc.summary = simple_summary(extracted_text)

        doc.status = "completed"
        doc.save()

        # Create chunks
        DocumentChunk.objects.filter(document=doc).delete()
        chunks = split_into_chunks(extracted_text)

        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk.objects.create(
                document=doc,
                chunk_index=i,
                content=chunk_text,
                metadata={"position": i, "total_chunks": len(chunks)},
            )
            # Trigger embedding generation
            update_chunk_embedding.delay(chunk.pk)

        logger.info(f"Processed document {document_id}: {len(chunks)} chunks")

    except Exception as e:
        logger.error(f"Failed to process document {document_id}: {e}")
        doc.status = "failed"
        doc.error_message = str(e)
        doc.save()
        raise self.retry(exc=e, countdown=60)
