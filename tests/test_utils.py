"""Tests for core utilities."""

import pytest
from core.utils import mask_pii, truncate_text, extract_keywords, simple_summary, calculate_token_estimate


class TestMaskPII:
    """Tests for PII masking function."""

    def test_mask_email(self):
        text = "連絡先は test@example.com です"
        result = mask_pii(text)
        assert "[EMAIL]" in result
        assert "test@example.com" not in result

    def test_mask_phone_japanese(self):
        text = "電話番号は 090-1234-5678 です"
        result = mask_pii(text)
        assert "[PHONE]" in result
        assert "090-1234-5678" not in result

    def test_mask_credit_card(self):
        text = "カード番号 1234-5678-9012-3456"
        result = mask_pii(text)
        assert "[CREDIT_CARD]" in result
        assert "1234-5678-9012-3456" not in result

    def test_mask_postal_code(self):
        text = "郵便番号 123-4567"
        result = mask_pii(text)
        assert "[POSTAL]" in result
        assert "123-4567" not in result

    def test_mask_id_number(self):
        text = "学籍番号 12345678901"
        result = mask_pii(text)
        assert "[ID_NUMBER]" in result

    def test_empty_text(self):
        assert mask_pii("") == ""
        assert mask_pii(None) is None


class TestTruncateText:
    """Tests for text truncation."""

    def test_short_text(self):
        text = "短いテキスト"
        assert truncate_text(text, 100) == text

    def test_long_text(self):
        text = "これは非常に長いテキストです。" * 20
        result = truncate_text(text, 50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_empty_text(self):
        assert truncate_text("") == ""


class TestExtractKeywords:
    """Tests for keyword extraction."""

    def test_basic_extraction(self):
        text = "Python programming is great. Python is powerful."
        keywords = extract_keywords(text)
        assert "python" in keywords
        assert "programming" in keywords

    def test_empty_text(self):
        assert extract_keywords("") == []

    def test_max_keywords(self):
        text = "apple banana cherry date elderberry fig grape"
        keywords = extract_keywords(text, max_keywords=3)
        assert len(keywords) <= 3


class TestSimpleSummary:
    """Tests for simple summary."""

    def test_basic_summary(self):
        text = "これは最初の文です。二番目の文です。三番目の文です。四番目の文です。"
        summary = simple_summary(text, max_sentences=2)
        assert "最初" in summary
        assert "二番目" in summary

    def test_empty_text(self):
        assert simple_summary("") == ""


class TestTokenEstimate:
    """Tests for token estimation."""

    def test_basic_estimate(self):
        text = "Hello world"
        estimate = calculate_token_estimate(text)
        assert estimate > 0

    def test_empty_text(self):
        assert calculate_token_estimate("") == 0
