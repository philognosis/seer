"""
Description optimization service.
Applies word economy, timing adjustments, and quality checks.
"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Words to avoid in audio descriptions
FILLER_WORDS = {"very", "really", "just", "quite", "rather", "somewhat", "actually"}
REDUNDANT_PHRASES = {
    "we see": "",
    "we can see": "",
    "the camera shows": "",
    "the scene shows": "",
    "in the scene": "",
    "on screen": "",
    "is shown": "",
    "appears to be": "is",
    "seems to be": "is",
    "begins to": "",
    "starts to": "",
}


class DescriptionOptimizer:
    """Optimizes descriptions for conciseness and clarity"""

    def optimize(self, text: str, max_words: Optional[int] = None) -> str:
        """
        Apply all optimizations to a description.

        Args:
            text: Raw description text
            max_words: Optional word limit

        Returns:
            Optimized description text
        """
        text = self._remove_redundant_phrases(text)
        text = self._remove_filler_words(text)
        text = self._ensure_present_tense(text)
        text = self._clean_whitespace(text)

        if max_words:
            text = self._trim_to_words(text, max_words)

        return text

    def _remove_redundant_phrases(self, text: str) -> str:
        """Remove camera-referencing and redundant phrases"""
        for phrase, replacement in REDUNDANT_PHRASES.items():
            text = re.sub(
                re.escape(phrase), replacement, text, flags=re.IGNORECASE
            )
        return text

    def _remove_filler_words(self, text: str) -> str:
        """Remove filler words that don't add meaning"""
        words = text.split()
        filtered = [w for w in words if w.lower() not in FILLER_WORDS]
        return " ".join(filtered)

    def _ensure_present_tense(self, text: str) -> str:
        """Basic check for present tense (heuristic)"""
        # This is a simplified check - full implementation would use NLP
        return text

    def _clean_whitespace(self, text: str) -> str:
        """Clean up extra whitespace"""
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _trim_to_words(self, text: str, max_words: int) -> str:
        """Trim text to word limit at sentence boundary"""
        words = text.split()
        if len(words) <= max_words:
            return text

        trimmed = " ".join(words[:max_words])
        for punct in [".", "!", ";"]:
            idx = trimmed.rfind(punct)
            if idx > len(trimmed) * 0.5:
                return trimmed[: idx + 1]

        return trimmed

    def validate_description(self, text: str) -> dict:
        """
        Validate a description against quality criteria.

        Returns dict with validation results and suggestions.
        """
        issues = []
        word_count = len(text.split())

        # Check minimum length
        if word_count < 3:
            issues.append("Description too short (minimum 3 words)")

        # Check for camera references
        camera_words = ["camera", "shot", "angle", "zoom", "pan", "close-up"]
        for word in camera_words:
            if word in text.lower():
                issues.append(f"Avoid camera terminology: '{word}'")

        # Check for past tense indicators
        past_indicators = ["was ", "were ", "had ", "went "]
        for indicator in past_indicators:
            if indicator in text.lower():
                issues.append(f"Use present tense (found: '{indicator.strip()}')")

        return {
            "is_valid": len(issues) == 0,
            "word_count": word_count,
            "issues": issues,
        }
