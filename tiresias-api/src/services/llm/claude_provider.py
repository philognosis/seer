"""
Anthropic Claude LLM provider implementation
"""
import logging
from typing import Optional

import anthropic

from src.core.exceptions import LLMProviderError
from src.core.settings import get_settings
from src.services.llm.provider_base import LLMProvider

logger = logging.getLogger(__name__)
settings = get_settings()


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        if not self.api_key:
            raise LLMProviderError(
                "Anthropic API key not configured", provider="claude"
            )
        self.client = anthropic.Anthropic(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "claude"

    @property
    def model_name(self) -> str:
        return "claude-sonnet-4-20250514"

    async def analyze_image(
        self,
        image_data: str,
        prompt: str,
        mime_type: str = "image/jpeg",
    ) -> dict:
        """Analyze image using Claude vision"""
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
            )

            return self._parse_json_response(message.content[0].text)

        except anthropic.APIError as e:
            raise LLMProviderError(
                f"Claude image analysis failed: {e}",
                provider="claude",
            )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using Claude"""
        try:
            kwargs = {
                "model": self.model_name,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            message = self.client.messages.create(**kwargs)
            return message.content[0].text

        except anthropic.APIError as e:
            raise LLMProviderError(
                f"Claude text generation failed: {e}",
                provider="claude",
            )
