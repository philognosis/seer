"""
Audio transcription service using Whisper
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.core.exceptions import VideoProcessingError

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionSegment:
    """A segment of transcribed speech"""

    start_time: float
    end_time: float
    text: str
    confidence: float
    words: list[dict]  # Word-level timestamps


@dataclass
class TranscriptionResult:
    """Full transcription result"""

    segments: list[TranscriptionSegment]
    language: str
    full_text: str
    duration: float


class TranscriptionService:
    """Transcribes audio using OpenAI Whisper"""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    def _load_model(self) -> None:
        """Lazy load Whisper model"""
        if self._model is None:
            import whisper

            self._model = whisper.load_model(self.model_size)
            logger.info(f"Loaded Whisper model: {self.model_size}")

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        progress_callback: Optional[callable] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio with word-level timestamps.

        Args:
            audio_path: Path to audio file
            language: Optional language code (auto-detect if None)
            progress_callback: Optional progress callback

        Returns:
            TranscriptionResult with segments and word-level timestamps
        """
        path = Path(audio_path)
        if not path.exists():
            raise VideoProcessingError(f"Audio file not found: {audio_path}")

        self._load_model()

        try:
            result = self._model.transcribe(
                str(path),
                language=language,
                word_timestamps=True,
                verbose=False,
            )

            segments = []
            for seg in result.get("segments", []):
                words = []
                for word_info in seg.get("words", []):
                    words.append(
                        {
                            "word": word_info.get("word", ""),
                            "start": word_info.get("start", 0),
                            "end": word_info.get("end", 0),
                            "probability": word_info.get("probability", 0),
                        }
                    )

                segments.append(
                    TranscriptionSegment(
                        start_time=seg["start"],
                        end_time=seg["end"],
                        text=seg["text"].strip(),
                        confidence=seg.get("avg_logprob", 0),
                        words=words,
                    )
                )

            full_text = " ".join(s.text for s in segments)
            duration = segments[-1].end_time if segments else 0

            logger.info(
                f"Transcribed {len(segments)} segments, "
                f"language: {result.get('language', 'unknown')}"
            )

            return TranscriptionResult(
                segments=segments,
                language=result.get("language", "en"),
                full_text=full_text,
                duration=duration,
            )

        except Exception as e:
            raise VideoProcessingError(f"Transcription failed: {e}")
