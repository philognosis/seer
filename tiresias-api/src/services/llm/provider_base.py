"""
Abstract base class for LLM providers
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider"""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model identifier"""
        ...

    @abstractmethod
    async def analyze_image(
        self,
        image_data: str,
        prompt: str,
        mime_type: str = "image/jpeg",
    ) -> dict:
        """
        Analyze an image using the LLM's vision capabilities.

        Args:
            image_data: Base64 encoded image data
            prompt: Analysis prompt
            mime_type: Image MIME type

        Returns:
            Analysis results as dict
        """
        ...

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum response tokens
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        ...

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks"""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {text[:200]}")
            return {"raw_text": text, "parse_error": True}
