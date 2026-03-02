"""
Frame extraction service using OpenCV
"""
import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from src.core.exceptions import VideoProcessingError
from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FrameExtractor:
    """Extracts key frames from video scenes"""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or settings.TEMP_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def extract_key_frames(
        self,
        video_path: str,
        timestamps: list[float],
        video_id: str,
    ) -> list[dict]:
        """
        Extract frames at specific timestamps.

        Args:
            video_path: Path to the video file
            timestamps: List of timestamps (seconds) to extract frames from
            video_id: Video ID for organizing output

        Returns:
            List of dicts with frame info (path, timestamp, dimensions)
        """
        path = Path(video_path)
        if not path.exists():
            raise VideoProcessingError(f"Video file not found: {video_path}")

        output_subdir = self.output_dir / video_id / "frames"
        output_subdir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise VideoProcessingError(f"Failed to open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = []

        try:
            for i, timestamp in enumerate(timestamps):
                frame_number = int(timestamp * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = cap.read()

                if not ret:
                    logger.warning(f"Failed to read frame at timestamp {timestamp}")
                    continue

                frame_path = output_subdir / f"frame_{i:04d}_{timestamp:.2f}s.jpg"
                cv2.imwrite(str(frame_path), frame)

                height, width = frame.shape[:2]
                frames.append(
                    {
                        "path": str(frame_path),
                        "timestamp": timestamp,
                        "frame_number": frame_number,
                        "width": width,
                        "height": height,
                    }
                )

            logger.info(f"Extracted {len(frames)} frames from {video_path}")
            return frames

        finally:
            cap.release()

    async def extract_scene_frames(
        self,
        video_path: str,
        scenes: list,
        video_id: str,
        frames_per_scene: int = 3,
    ) -> list[dict]:
        """
        Extract key frames from detected scenes.

        Extracts frames at the start, middle, and end of each scene.
        """
        timestamps = []
        for scene in scenes:
            start = scene.start_time
            end = scene.end_time
            mid = (start + end) / 2

            if frames_per_scene >= 3:
                timestamps.extend([start, mid, end])
            elif frames_per_scene == 2:
                timestamps.extend([start, end])
            else:
                timestamps.append(mid)

        return await self.extract_key_frames(video_path, timestamps, video_id)

    async def get_video_metadata(self, video_path: str) -> dict:
        """Get video metadata using OpenCV"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoProcessingError(f"Failed to open video: {video_path}")

        try:
            return {
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
                "codec": int(cap.get(cv2.CAP_PROP_FOURCC)),
            }
        finally:
            cap.release()
