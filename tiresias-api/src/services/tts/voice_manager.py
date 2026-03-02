"""
Voice management service.
Handles voice selection, fallback, and preference management.
"""
import logging
from typing import Optional

from src.core.settings import get_settings
from src.services.tts.elevenlabs_tts import ElevenLabsTTS
from src.services.tts.polly_tts import PollyTTS

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceManager:
    """Manages TTS voice selection and synthesis"""

    AVAILABLE_VOICES = {
        "female_us": {"name": "Sarah", "accent": "US English", "gender": "Female"},
        "male_us": {"name": "James", "accent": "US English", "gender": "Male"},
        "female_uk": {"name": "Emma", "accent": "UK English", "gender": "Female"},
        "male_uk": {"name": "William", "accent": "UK English", "gender": "Male"},
    }

    def __init__(self):
        self._elevenlabs: Optional[ElevenLabsTTS] = None
        self._polly: Optional[PollyTTS] = None

    def _get_elevenlabs(self) -> Optional[ElevenLabsTTS]:
        """Lazy initialize ElevenLabs client"""
        if self._elevenlabs is None and settings.ELEVENLABS_API_KEY:
            try:
                self._elevenlabs = ElevenLabsTTS()
            except Exception as e:
                logger.warning(f"ElevenLabs unavailable: {e}")
        return self._elevenlabs

    def _get_polly(self) -> Optional[PollyTTS]:
        """Lazy initialize AWS Polly client"""
        if self._polly is None and settings.AWS_ACCESS_KEY_ID:
            try:
                self._polly = PollyTTS()
            except Exception as e:
                logger.warning(f"AWS Polly unavailable: {e}")
        return self._polly

    async def synthesize(
        self,
        text: str,
        voice_id: str = "female_us",
        output_path: str = "",
        speed: float = 1.0,
    ) -> str:
        """
        Synthesize speech with automatic fallback.

        Tries ElevenLabs first, falls back to AWS Polly.
        """
        # Validate voice
        if voice_id not in self.AVAILABLE_VOICES:
            logger.warning(f"Unknown voice '{voice_id}', using 'female_us'")
            voice_id = "female_us"

        # Try ElevenLabs first
        elevenlabs = self._get_elevenlabs()
        if elevenlabs:
            try:
                return await elevenlabs.synthesize(
                    text=text,
                    voice_id=voice_id,
                    output_path=output_path,
                    speed=speed,
                )
            except Exception as e:
                logger.warning(f"ElevenLabs failed, falling back to Polly: {e}")

        # Fallback to AWS Polly
        polly = self._get_polly()
        if polly:
            return await polly.synthesize(
                text=text,
                voice_id=voice_id,
                output_path=output_path,
                speed=speed,
            )

        raise RuntimeError("No TTS provider available")

    def get_available_voices(self) -> list[dict]:
        """Get list of available voices"""
        return [
            {"id": vid, **info} for vid, info in self.AVAILABLE_VOICES.items()
        ]
