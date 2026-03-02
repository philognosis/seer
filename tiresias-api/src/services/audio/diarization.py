"""
Speaker diarization service using pyannote.audio
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.core.exceptions import VideoProcessingError
from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class SpeakerSegment:
    """A segment attributed to a specific speaker"""

    start_time: float
    end_time: float
    speaker_id: str
    duration: float


class DiarizationService:
    """Speaker diarization using pyannote.audio"""

    def __init__(self):
        self._pipeline = None

    def _load_pipeline(self) -> None:
        """Lazy load diarization pipeline"""
        if self._pipeline is None:
            try:
                from pyannote.audio import Pipeline

                self._pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=settings.HUGGINGFACE_TOKEN,
                )
                logger.info("Loaded pyannote diarization pipeline")
            except Exception as e:
                logger.warning(f"Failed to load diarization pipeline: {e}")
                raise VideoProcessingError(
                    "Diarization pipeline unavailable. "
                    "Ensure HUGGINGFACE_TOKEN is set and pyannote.audio is installed."
                )

    async def diarize(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
    ) -> list[SpeakerSegment]:
        """
        Perform speaker diarization on audio.

        Args:
            audio_path: Path to audio file
            num_speakers: Optional known number of speakers

        Returns:
            List of SpeakerSegment objects
        """
        path = Path(audio_path)
        if not path.exists():
            raise VideoProcessingError(f"Audio file not found: {audio_path}")

        self._load_pipeline()

        try:
            diarization_params = {}
            if num_speakers is not None:
                diarization_params["num_speakers"] = num_speakers

            diarization = self._pipeline(str(path), **diarization_params)

            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append(
                    SpeakerSegment(
                        start_time=turn.start,
                        end_time=turn.end,
                        speaker_id=speaker,
                        duration=turn.end - turn.start,
                    )
                )

            logger.info(
                f"Diarization found {len(set(s.speaker_id for s in segments))} speakers "
                f"in {len(segments)} segments"
            )
            return segments

        except Exception as e:
            raise VideoProcessingError(f"Diarization failed: {e}")
