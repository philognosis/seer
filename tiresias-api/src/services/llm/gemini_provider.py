"""
Google Gemini LLM provider implementation
"""
import logging
from typing import Optional

import google.generativeai as genai

from src.core.exceptions import LLMProviderError
from src.core.settings import get_settings
from src.services.llm.provider_base import LLMProvider

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiProvider(LLMProvider):
    """Google Gemini 2.0 Flash provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise LLMProviderError(
                "Gemini API key not configured", provider="gemini"
            )
        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel("gemini-2.0-flash")
        self._vision_model = genai.GenerativeModel("gemini-2.0-flash")

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return "gemini-2.0-flash"

    async def analyze_image(
        self,
        image_data: str,
        prompt: str,
        mime_type: str = "image/jpeg",
    ) -> dict:
        """Analyze image using Gemini vision"""
        try:
            import base64

            image_bytes = base64.b64decode(image_data)

            response = self._vision_model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": mime_type,
                        "data": image_bytes,
                    },
                ],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=2048,
                ),
            )

            return self._parse_json_response(response.text)

        except Exception as e:
            raise LLMProviderError(
                f"Gemini image analysis failed: {e}",
                provider="gemini",
            )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using Gemini"""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = self._model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            return response.text

        except Exception as e:
            raise LLMProviderError(
                f"Gemini text generation failed: {e}",
                provider="gemini",
            )
