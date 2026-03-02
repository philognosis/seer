"""
OpenAI GPT-4 LLM provider implementation
"""
import logging
from typing import Optional

import openai

from src.core.exceptions import LLMProviderError
from src.core.settings import get_settings
from src.services.llm.provider_base import LLMProvider

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise LLMProviderError(
                "OpenAI API key not configured", provider="openai"
            )
        self.client = openai.OpenAI(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return "gpt-4o"

    async def analyze_image(
        self,
        image_data: str,
        prompt: str,
        mime_type: str = "image/jpeg",
    ) -> dict:
        """Analyze image using GPT-4 Vision"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=2048,
                temperature=0.4,
            )

            return self._parse_json_response(response.choices[0].message.content)

        except openai.APIError as e:
            raise LLMProviderError(
                f"OpenAI image analysis failed: {e}",
                provider="openai",
            )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using GPT-4"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content

        except openai.APIError as e:
            raise LLMProviderError(
                f"OpenAI text generation failed: {e}",
                provider="openai",
            )
