"""Tests for LLM provider."""

import pytest
from unittest.mock import patch, MagicMock


class TestLLMProvider:
    """Tests for LLM provider."""

    def test_is_available_without_key(self):
        from core.llm import LLMProvider

        with patch("core.llm.settings") as mock_settings:
            mock_settings.LLM_ENABLED = True
            mock_settings.LLM_API_KEY = ""
            mock_settings.LLM_BASE_URL = "https://api.openai.com/v1"
            mock_settings.LLM_MODEL = "gpt-4"
            mock_settings.EMBEDDING_MODEL = "text-embedding-3-small"

            provider = LLMProvider()
            assert provider.is_available() is False

    def test_generate_digest_fallback(self):
        from core.llm import LLMProvider

        with patch("core.llm.settings") as mock_settings:
            mock_settings.LLM_ENABLED = False
            mock_settings.LLM_API_KEY = ""
            mock_settings.LLM_BASE_URL = ""
            mock_settings.LLM_MODEL = ""
            mock_settings.EMBEDDING_MODEL = ""

            provider = LLMProvider()
            result = provider.generate_digest("これはテストテキストです。重要な情報が含まれています。")

            assert "summary" in result
            assert "tags" in result
            assert isinstance(result["tags"], list)

    def test_generate_assistant_response_fallback(self):
        from core.llm import LLMProvider

        with patch("core.llm.settings") as mock_settings:
            mock_settings.LLM_ENABLED = False
            mock_settings.LLM_API_KEY = ""
            mock_settings.LLM_BASE_URL = ""
            mock_settings.LLM_MODEL = ""
            mock_settings.EMBEDDING_MODEL = ""

            provider = LLMProvider()
            result = provider.generate_assistant_response(
                question="テスト質問",
                context_items=[],
                preferences=[],
            )

            assert "answer" in result
            assert "LLMが有効化されていない" in result["answer"]
