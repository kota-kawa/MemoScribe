"""
Core utility functions for MemoScribe.
"""

import re
from typing import Optional


def mask_pii(text: str) -> str:
    """
    Mask personally identifiable information in text.
    Replaces emails, phone numbers, addresses, credit cards, and ID-like numbers.
    """
    if not text:
        return text

    # Email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", text)

    # Japanese phone numbers (various formats)
    text = re.sub(r"\b0\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4}\b", "[PHONE]", text)
    # International format
    text = re.sub(r"\+\d{1,3}[-\s]?\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4}", "[PHONE]", text)

    # Credit card numbers (16 digits with optional separators)
    text = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CREDIT_CARD]", text)

    # Japanese postal codes
    text = re.sub(r"\b\d{3}[-]?\d{4}\b", "[POSTAL]", text)

    # ID-like numbers (8+ consecutive digits)
    text = re.sub(r"\b\d{8,}\b", "[ID_NUMBER]", text)

    # My Number (Japanese social security - 12 digits)
    text = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[MY_NUMBER]", text)

    return text


def truncate_text(text: str, max_length: int = 300) -> str:
    """Truncate text to max_length with ellipsis."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def extract_keywords(text: str, max_keywords: int = 5) -> list[str]:
    """
    Simple keyword extraction based on word frequency.
    Used when LLM is disabled.
    """
    if not text:
        return []

    # Remove common Japanese particles and stopwords
    stopwords = {
        "の", "は", "が", "を", "に", "で", "と", "も", "や", "へ", "から", "まで",
        "より", "など", "か", "て", "た", "だ", "です", "ます", "する", "ある", "いる",
        "これ", "それ", "あれ", "この", "その", "あの", "こと", "もの", "ため",
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
        "may", "might", "can", "of", "in", "to", "for", "with", "on", "at", "by",
        "from", "as", "into", "through", "during", "before", "after", "above", "below",
        "and", "or", "but", "if", "then", "else", "when", "up", "down", "out", "off",
    }

    # Tokenize (simple split for now)
    words = re.findall(r"\b\w{2,}\b", text.lower())

    # Count frequency excluding stopwords
    word_counts: dict[str, int] = {}
    for word in words:
        if word not in stopwords and not word.isdigit():
            word_counts[word] = word_counts.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def simple_summary(text: str, max_sentences: int = 3) -> str:
    """
    Create a simple summary by extracting first few sentences.
    Used when LLM is disabled.
    """
    if not text:
        return ""

    # Split by sentence endings (Japanese and English)
    sentences = re.split(r"[。！？.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return truncate_text(text, 200)

    return "。".join(sentences[:max_sentences]) + "。" if sentences else ""


def calculate_token_estimate(text: str) -> int:
    """
    Estimate token count for a text.
    Rough estimate: ~0.7 tokens per character for mixed Japanese/English.
    """
    if not text:
        return 0
    # Japanese text tends to have ~0.5-1 tokens per character
    # English text tends to have ~0.25 tokens per word (~4 chars)
    # Use a middle ground estimate
    return int(len(text) * 0.7)
