"""
AWS Polly TTS fallback integration
"""
import logging
from pathlib import Path
from typing import Optional

import boto3

from src.core.exceptions import TTSProviderError
from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# AWS Polly voice IDs
POLLY_VOICE_MAP = {
    "female_us": "Joanna",
    "male_us": "Matthew",
    "female_uk": "Amy",
    "male_uk": "Brian",
}


class PollyTTS:
    """Text-to-speech using AWS Polly (fallback)"""

    def __init__(self):
        try:
            self.client = boto3.client(
                "polly",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
        except Exception as e:
            raise TTSProviderError(
                f"AWS Polly initialization failed: {e}",
                provider="polly",
            )

    async def synthesize(
        self,
        text: str,
        voice_id: str = "female_us",
        output_path: str = "",
        speed: float = 1.0,
    ) -> str:
        """
        Synthesize speech from text using AWS Polly.

        Args:
            text: Text to speak
            voice_id: Our voice identifier
            output_path: Where to save the audio file
            speed: Speed multiplier

        Returns:
            Path to generated audio file
        """
        polly_voice = POLLY_VOICE_MAP.get(voice_id, POLLY_VOICE_MAP["female_us"])

        # Wrap text in SSML for speed control
        rate_percent = int(speed * 100)
        ssml_text = (
            f'<speak><prosody rate="{rate_percent}%">{text}</prosody></speak>'
        )

        try:
            response = self.client.synthesize_speech(
                Text=ssml_text,
                TextType="ssml",
                OutputFormat="mp3",
                VoiceId=polly_voice,
                Engine="neural",
            )

            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)

            with open(output, "wb") as f:
                f.write(response["AudioStream"].read())

            logger.info(f"Polly synthesized: {len(text)} chars -> {output_path}")
            return str(output)

        except Exception as e:
            raise TTSProviderError(
                f"AWS Polly synthesis failed: {e}",
                provider="polly",
            )
