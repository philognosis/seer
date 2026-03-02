"""
Gap analysis and description fitting service.
Ensures descriptions fit perfectly within available gaps.
"""
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Average speaking rate for audio description (words per second)
SPEAKING_RATE_WPS = 2.5  # ~150 words per minute


@dataclass
class DescriptionSlot:
    """A slot where a description can be placed"""

    gap_start: float  # seconds
    gap_end: float  # seconds
    available_duration: float  # seconds
    max_words: int  # maximum words that fit
    priority: int  # higher = more important to fill
    scene_timestamp: float  # what moment this describes


class GapAnalyzer:
    """Analyzes gaps and determines optimal description placement"""

    def __init__(
        self,
        speaking_rate_wps: float = SPEAKING_RATE_WPS,
        padding: float = 0.2,  # padding at start/end of gap
    ):
        self.speaking_rate = speaking_rate_wps
        self.padding = padding

    def analyze_gaps(
        self,
        gaps: list,
        scene_analyses: list[dict],
    ) -> list[DescriptionSlot]:
        """
        Match available gaps with scene analyses to create description slots.

        Args:
            gaps: List of SilenceGap objects
            scene_analyses: List of scene analysis results with timestamps

        Returns:
            List of DescriptionSlot objects sorted by timestamp
        """
        slots = []

        for gap in gaps:
            # Find scenes that occur near this gap
            usable_start = gap.start_time + self.padding
            usable_end = gap.end_time - self.padding
            usable_duration = usable_end - usable_start

            if usable_duration < 1.0:
                continue

            max_words = int(usable_duration * self.speaking_rate)

            # Find the most relevant scene for this gap
            best_scene = self._find_best_scene(gap, scene_analyses)
            priority = self._calculate_priority(best_scene) if best_scene else 1

            slots.append(
                DescriptionSlot(
                    gap_start=usable_start,
                    gap_end=usable_end,
                    available_duration=usable_duration,
                    max_words=max_words,
                    priority=priority,
                    scene_timestamp=best_scene.get("timestamp", gap.start_time)
                    if best_scene
                    else gap.start_time,
                )
            )

        # Sort by priority (highest first), then by timestamp
        slots.sort(key=lambda s: (-s.priority, s.scene_timestamp))

        logger.info(f"Created {len(slots)} description slots")
        return slots

    def estimate_duration(self, text: str, speed_multiplier: float = 1.0) -> float:
        """Estimate how long it takes to speak a description"""
        words = len(text.split())
        return words / (self.speaking_rate * speed_multiplier)

    def trim_to_fit(self, text: str, max_duration: float, speed: float = 1.0) -> str:
        """Trim description text to fit within duration limit"""
        words = text.split()
        max_words = int(max_duration * self.speaking_rate * speed)

        if len(words) <= max_words:
            return text

        # Trim and add ellipsis-free ending
        trimmed = " ".join(words[:max_words])
        # Try to end at a sentence boundary
        for punct in [".", "!", ";", ","]:
            last_idx = trimmed.rfind(punct)
            if last_idx > len(trimmed) * 0.5:
                return trimmed[: last_idx + 1]

        return trimmed

    def _find_best_scene(
        self, gap: object, scenes: list[dict]
    ) -> Optional[dict]:
        """Find the scene analysis most relevant to a gap"""
        best = None
        best_distance = float("inf")

        for scene in scenes:
            timestamp = scene.get("timestamp", 0)
            # Prefer scenes that just happened before the gap
            distance = gap.start_time - timestamp
            if 0 <= distance < best_distance:
                best = scene
                best_distance = distance

        return best

    def _calculate_priority(self, scene: dict) -> int:
        """Calculate priority based on scene analysis"""
        importance = scene.get("narrative_importance", "medium")
        priority_map = {"high": 10, "medium": 5, "low": 2}
        return priority_map.get(importance, 5)
