"""
Scene detection service using PySceneDetect
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from scenedetect import ContentDetector, SceneManager, open_video

from src.core.exceptions import VideoProcessingError

logger = logging.getLogger(__name__)


@dataclass
class Scene:
    """Represents a detected scene"""

    start_time: float  # seconds
    end_time: float  # seconds
    duration: float  # seconds
    scene_number: int


class SceneDetectorService:
    """Detects scene changes in videos using PySceneDetect"""

    def __init__(
        self,
        threshold: float = 27.0,
        min_scene_len: int = 15,
    ):
        self.threshold = threshold
        self.min_scene_len = min_scene_len

    async def detect_scenes(
        self,
        video_path: str,
        progress_callback: Optional[callable] = None,
    ) -> list[Scene]:
        """
        Detect scene changes in a video.

        Args:
            video_path: Path to the video file
            progress_callback: Optional callback for progress updates

        Returns:
            List of detected scenes with timestamps
        """
        path = Path(video_path)
        if not path.exists():
            raise VideoProcessingError(f"Video file not found: {video_path}")

        try:
            video = open_video(str(path))
            scene_manager = SceneManager()
            scene_manager.add_detector(
                ContentDetector(
                    threshold=self.threshold,
                    min_scene_len=self.min_scene_len,
                )
            )

            scene_manager.detect_scenes(video)
            scene_list = scene_manager.get_scene_list()

            scenes = []
            for i, (start, end) in enumerate(scene_list):
                start_sec = start.get_seconds()
                end_sec = end.get_seconds()
                scenes.append(
                    Scene(
                        start_time=start_sec,
                        end_time=end_sec,
                        duration=end_sec - start_sec,
                        scene_number=i + 1,
                    )
                )

            logger.info(f"Detected {len(scenes)} scenes in {video_path}")
            return scenes

        except Exception as e:
            raise VideoProcessingError(
                f"Scene detection failed: {e}",
                details={"video_path": video_path},
            )
