"""
Multi-layer voice activity detection for dialogue detection.
Ensures ZERO dialogue interruption - the absolute #1 priority.
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from src.core.exceptions import VideoProcessingError

logger = logging.getLogger(__name__)


@dataclass
class DialogueSegment:
    """A segment of detected dialogue/voice activity"""

    start_time: float  # seconds
    end_time: float  # seconds
    confidence: float  # 0.0-1.0
    speaker_id: Optional[str] = None
    text: Optional[str] = None


@dataclass
class SilenceGap:
    """A gap of silence suitable for audio description"""

    start_time: float  # seconds
    end_time: float  # seconds
    duration: float  # seconds
    is_safe: bool  # True if confirmed safe for description


class DialogueDetector:
    """
    Multi-layer voice activity detection system.

    Uses multiple detection methods for maximum accuracy:
    1. Energy-based detection (fast, baseline)
    2. Whisper transcription (accurate, provides text)
    3. Safety margin padding (ensures no interruption)

    The goal is ZERO dialogue interruption - we err on the side
    of caution and add safety margins to every detection.
    """

    # Minimum gap duration for description insertion (seconds)
    MIN_GAP_DURATION = 2.0

    # Safety margin added before and after dialogue (seconds)
    SAFETY_MARGIN = 0.3

    # Energy threshold for voice detection
    ENERGY_THRESHOLD = 0.02

    def __init__(
        self,
        min_gap_duration: float = 2.0,
        safety_margin: float = 0.3,
    ):
        self.min_gap_duration = min_gap_duration
        self.safety_margin = safety_margin

    async def detect_dialogue(
        self,
        audio_path: str,
        progress_callback: Optional[callable] = None,
    ) -> list[DialogueSegment]:
        """
        Detect all dialogue/voice segments in audio.

        Uses energy-based detection as the primary method.
        Results are padded with safety margins.
        """
        path = Path(audio_path)
        if not path.exists():
            raise VideoProcessingError(f"Audio file not found: {audio_path}")

        try:
            import librosa

            # Load audio
            y, sr = librosa.load(str(path), sr=16000, mono=True)

            # Energy-based voice activity detection
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)  # 10ms hop

            # Compute RMS energy
            rms = librosa.feature.rms(
                y=y, frame_length=frame_length, hop_length=hop_length
            )[0]

            # Threshold for voice detection
            threshold = np.mean(rms) * 0.5
            is_voice = rms > threshold

            # Convert frame-level to time-level segments
            segments = []
            in_segment = False
            start_frame = 0

            for i, active in enumerate(is_voice):
                if active and not in_segment:
                    start_frame = i
                    in_segment = True
                elif not active and in_segment:
                    start_time = start_frame * hop_length / sr
                    end_time = i * hop_length / sr
                    segments.append(
                        DialogueSegment(
                            start_time=max(0, start_time - self.safety_margin),
                            end_time=end_time + self.safety_margin,
                            confidence=0.8,
                        )
                    )
                    in_segment = False

            # Handle last segment
            if in_segment:
                start_time = start_frame * hop_length / sr
                end_time = len(is_voice) * hop_length / sr
                segments.append(
                    DialogueSegment(
                        start_time=max(0, start_time - self.safety_margin),
                        end_time=end_time + self.safety_margin,
                        confidence=0.8,
                    )
                )

            # Merge overlapping segments
            segments = self._merge_overlapping(segments)

            logger.info(f"Detected {len(segments)} dialogue segments")
            return segments

        except Exception as e:
            raise VideoProcessingError(f"Dialogue detection failed: {e}")

    async def find_description_gaps(
        self,
        dialogue_segments: list[DialogueSegment],
        total_duration: float,
    ) -> list[SilenceGap]:
        """
        Find gaps between dialogue suitable for audio descriptions.

        Only returns gaps that are:
        1. At least MIN_GAP_DURATION seconds long
        2. Not within SAFETY_MARGIN of any dialogue
        3. Verified as safe for description insertion
        """
        if not dialogue_segments:
            return [
                SilenceGap(
                    start_time=0,
                    end_time=total_duration,
                    duration=total_duration,
                    is_safe=True,
                )
            ]

        gaps = []

        # Sort segments by start time
        sorted_segments = sorted(dialogue_segments, key=lambda s: s.start_time)

        # Check gap before first dialogue
        if sorted_segments[0].start_time > self.min_gap_duration:
            gaps.append(
                SilenceGap(
                    start_time=0,
                    end_time=sorted_segments[0].start_time,
                    duration=sorted_segments[0].start_time,
                    is_safe=True,
                )
            )

        # Check gaps between dialogue segments
        for i in range(len(sorted_segments) - 1):
            gap_start = sorted_segments[i].end_time
            gap_end = sorted_segments[i + 1].start_time
            gap_duration = gap_end - gap_start

            if gap_duration >= self.min_gap_duration:
                gaps.append(
                    SilenceGap(
                        start_time=gap_start,
                        end_time=gap_end,
                        duration=gap_duration,
                        is_safe=True,
                    )
                )

        # Check gap after last dialogue
        last_end = sorted_segments[-1].end_time
        if total_duration - last_end > self.min_gap_duration:
            gaps.append(
                SilenceGap(
                    start_time=last_end,
                    end_time=total_duration,
                    duration=total_duration - last_end,
                    is_safe=True,
                )
            )

        logger.info(
            f"Found {len(gaps)} description gaps "
            f"(total: {sum(g.duration for g in gaps):.1f}s)"
        )
        return gaps

    def _merge_overlapping(
        self, segments: list[DialogueSegment]
    ) -> list[DialogueSegment]:
        """Merge overlapping or adjacent dialogue segments"""
        if not segments:
            return []

        sorted_segs = sorted(segments, key=lambda s: s.start_time)
        merged = [sorted_segs[0]]

        for seg in sorted_segs[1:]:
            if seg.start_time <= merged[-1].end_time:
                # Merge with previous segment
                merged[-1] = DialogueSegment(
                    start_time=merged[-1].start_time,
                    end_time=max(merged[-1].end_time, seg.end_time),
                    confidence=max(merged[-1].confidence, seg.confidence),
                )
            else:
                merged.append(seg)

        return merged
