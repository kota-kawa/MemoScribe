"""
LLM provider abstraction for MemoScribe.
Supports OpenAI-compatible APIs.
"""

import json
import logging
from typing import Any, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class LLMProvider:
    """Abstract LLM provider supporting OpenAI-compatible APIs."""

    def __init__(self):
        self.enabled = settings.LLM_ENABLED
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL
        self._client = None

    @property
    def client(self):
        """Lazy load OpenAI client."""
        if self._client is None and self.enabled and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self._client = None
        return self._client

    def is_available(self) -> bool:
        """Check if LLM is available and configured."""
        return self.enabled and bool(self.api_key) and self.client is not None

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Optional[str]:
        """
        Generate a chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Generated text or None if failed
        """
        if not self.is_available():
            logger.warning("LLM not available, returning None")
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return None

    def generate_embedding(self, text: str) -> Optional[list[float]]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if failed
        """
        if not self.is_available():
            logger.warning("LLM not available for embedding")
            return None

        if not text or not text.strip():
            return None

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text[:8000],  # Truncate to avoid token limits
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def generate_digest(self, text: str) -> dict[str, Any]:
        """
        Generate a digest (summary, tags, topics, actions) from text.

        Returns:
            Dict with summary, tags, topics, actions
        """
        if not self.is_available():
            # Fallback to simple extraction
            from core.utils import simple_summary, extract_keywords
            return {
                "summary": simple_summary(text),
                "tags": extract_keywords(text),
                "topics": extract_keywords(text, max_keywords=3),
                "actions": [],
            }

        system_prompt = """あなたは個人の記録を整理する秘書です。
与えられたテキストから以下を抽出してJSON形式で返してください：

{
    "summary": "2-3文の要約",
    "tags": ["タグ1", "タグ2", "タグ3"],
    "topics": ["主要トピック1", "主要トピック2"],
    "actions": ["アクション1", "アクション2"]（もしあれば）
}

- 要約は事実のみを含め、推測しないこと
- タグは3-5個程度
- アクションは明示的に書かれているものだけ抽出
"""

        try:
            response = self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text[:4000]},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            if response:
                # Try to parse JSON from response
                # Handle markdown code blocks
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    cleaned = "\n".join(lines[1:-1])

                return json.loads(cleaned)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Digest generation failed: {e}")

        # Fallback
        from core.utils import simple_summary, extract_keywords
        return {
            "summary": simple_summary(text),
            "tags": extract_keywords(text),
            "topics": extract_keywords(text, max_keywords=3),
            "actions": [],
        }

    def generate_assistant_response(
        self,
        question: str,
        context_items: list[dict],
        preferences: list[dict],
    ) -> dict[str, Any]:
        """
        Generate an assistant response with citations.

        Args:
            question: User's question
            context_items: Retrieved context items with id, type, title, content
            preferences: User preferences

        Returns:
            Dict with answer, next_questions, citations
        """
        if not self.is_available():
            return {
                "answer": "LLMが有効化されていないため、回答を生成できません。設定からLLMを有効化してください。",
                "next_questions": [],
                "citations": [],
            }

        # Build context string with citation markers
        context_str = ""
        for i, item in enumerate(context_items):
            context_str += f"\n[{i+1}] ({item['type']}) {item['title']}:\n{item['content'][:500]}\n"

        # Build preferences string
        pref_str = ""
        if preferences:
            pref_str = "\nユーザーの好み/ポリシー:\n"
            for pref in preferences:
                pref_str += f"- {pref['key']}: {pref['value']}\n"

        system_prompt = f"""あなたは個人専用の秘書です。以下のルールを厳守してください：

1. 根拠のない断定は禁止。提供されたコンテキストに基づいてのみ回答する。
2. コンテキストにない情報は創作しない。不明な点は明示する。
3. 情報が不足している場合は、追加質問を列挙する。
4. 丁寧で現実的な回答を心がける。
{pref_str}

回答は以下のJSON形式で返してください：
{{
    "answer": "回答本文（根拠を[1][2]のように引用番号で示す）",
    "next_questions": ["追加で必要な質問1", "追加で必要な質問2"],
    "citations": [
        {{"ref": 1, "type": "種類", "title": "タイトル", "quote": "引用部分"}}
    ]
}}

- answerでは、根拠となる情報源を[1]のように番号で参照する
- 根拠が不足している場合は「情報が不足しています」と明示
- citationsには実際に参照した情報のみを含める"""

        user_prompt = f"""質問: {question}

参照可能なコンテキスト:
{context_str if context_str else "（参照可能な情報がありません）"}
"""

        try:
            response = self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.5,
                max_tokens=1500,
            )

            if response:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    cleaned = "\n".join(lines[1:-1])

                result = json.loads(cleaned)

                # Validate structure
                if "answer" not in result:
                    result["answer"] = cleaned
                if "next_questions" not in result:
                    result["next_questions"] = []
                if "citations" not in result:
                    result["citations"] = []

                return result

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Assistant response failed: {e}")

        return {
            "answer": "申し訳ありません。回答の生成中にエラーが発生しました。",
            "next_questions": [],
            "citations": [],
        }

    def generate_writing(
        self,
        template_type: str,
        user_input: str,
        context_items: list[dict],
        preferences: list[dict],
    ) -> dict[str, Any]:
        """
        Generate writing based on template and context.

        Args:
            template_type: Type of writing (email_polite, email_casual, rewrite_short, etc.)
            user_input: User's input/request
            context_items: Retrieved context
            preferences: User preferences

        Returns:
            Dict with output, citations
        """
        if not self.is_available():
            return {
                "output": "LLMが有効化されていないため、文章を生成できません。",
                "citations": [],
            }

        template_prompts = {
            "email_polite": "丁寧なビジネスメールを作成してください。敬語を使用し、失礼のない文面にしてください。",
            "email_casual": "カジュアルなメールを作成してください。親しみやすいトーンで書いてください。",
            "rewrite_short": "以下の文章を簡潔に短くリライトしてください。要点を残しつつ、冗長な部分を削除してください。",
            "rewrite_polite": "以下の文章を丁寧な表現にリライトしてください。敬語を適切に使用してください。",
            "rewrite_logical": "以下の文章を論理的に整理してリライトしてください。構成を明確にしてください。",
            "daily_plan": "タスクとログから今日やるべきこと3つを提案してください。優先度と理由を添えてください。",
        }

        template_instruction = template_prompts.get(
            template_type,
            "以下の依頼に沿って文章を作成してください。"
        )

        # Build context
        context_str = ""
        for i, item in enumerate(context_items):
            context_str += f"\n[{i+1}] ({item['type']}) {item['title']}:\n{item['content'][:300]}\n"

        pref_str = ""
        if preferences:
            for pref in preferences:
                pref_str += f"- {pref['key']}: {pref['value']}\n"

        system_prompt = f"""あなたは文章作成をサポートする秘書です。

ルール：
1. 根拠にない事実は書かない（盛り禁止）
2. 必要な情報が不足している場合は、その旨を明示する
3. ユーザーの好みに沿った文体で書く
{f"ユーザーの好み: {pref_str}" if pref_str else ""}

タスク: {template_instruction}

回答はJSON形式で：
{{
    "output": "生成した文章",
    "citations": [{{"ref": 1, "quote": "参照した部分"}}],
    "missing_info": ["不足している情報"]
}}"""

        user_prompt = f"""依頼: {user_input}

参照情報:
{context_str if context_str else "（参照情報なし）"}"""

        try:
            response = self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.6,
                max_tokens=1500,
            )

            if response:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    cleaned = "\n".join(lines[1:-1])

                return json.loads(cleaned)

        except Exception as e:
            logger.error(f"Writing generation failed: {e}")

        return {
            "output": "文章の生成中にエラーが発生しました。",
            "citations": [],
        }


# Global instance
llm_provider = LLMProvider()
