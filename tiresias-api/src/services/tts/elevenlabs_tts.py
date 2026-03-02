"""
ElevenLabs TTS integration
"""
import logging
from pathlib import Path
from typing import Optional

from src.core.exceptions import TTSProviderError
from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ElevenLabs voice IDs mapped to our voice identifiers
VOICE_MAP = {
    "female_us": "21m00Tcm4TlvDq8ikWAM",  # Rachel
    "male_us": "VR6AewLTigWG4xSOukaG",  # Arnold
    "female_uk": "ThT5KcBeYPX3keUQqHPh",  # Dorothy
    "male_uk": "pNInz6obpgDQGcFmaJgB",  # Adam
}


class ElevenLabsTTS:
    """Text-to-speech using ElevenLabs API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ELEVENLABS_API_KEY
        if not self.api_key:
            raise TTSProviderError(
                "ElevenLabs API key not configured", provider="elevenlabs"
            )

    async def synthesize(
        self,
        text: str,
        voice_id: str = "female_us",
        output_path: str = "",
        speed: float = 1.0,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> str:
        """
        Synthesize speech from text.

        Args:
            text: Text to speak
            voice_id: Our voice identifier (e.g., 'female_us')
            output_path: Where to save the audio file
            speed: Speed multiplier (0.75-1.3)
            stability: Voice stability (0-1)
            similarity_boost: Voice similarity boost (0-1)

        Returns:
            Path to generated audio file
        """
        elevenlabs_voice_id = VOICE_MAP.get(voice_id, VOICE_MAP["female_us"])

        try:
            from elevenlabs import ElevenLabs

            client = ElevenLabs(api_key=self.api_key)

            audio = client.text_to_speech.convert(
                voice_id=elevenlabs_voice_id,
                text=text,
                model_id="eleven_turbo_v2_5",
                voice_settings={
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "speed": speed,
                },
            )

            # Save audio to file
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)

            with open(output, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            logger.info(f"Synthesized speech: {len(text)} chars -> {output_path}")
            return str(output)

        except Exception as e:
            raise TTSProviderError(
                f"ElevenLabs synthesis failed: {e}",
                provider="elevenlabs",
            )

    async def get_available_voices(self) -> list[dict]:
        """List available ElevenLabs voices"""
        try:
            from elevenlabs import ElevenLabs

            client = ElevenLabs(api_key=self.api_key)
            voices = client.voices.get_all()

            return [
                {
                    "voice_id": v.voice_id,
                    "name": v.name,
                    "category": v.category,
                }
                for v in voices.voices
            ]

        except Exception as e:
            logger.error(f"Failed to list ElevenLabs voices: {e}")
            return []
