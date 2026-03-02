"""
Audio mixing service using FFmpeg.
Handles ducking, crossfades, and final audio production.
"""
import logging
import subprocess
from pathlib import Path
from typing import Optional

from src.core.exceptions import VideoProcessingError
from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AudioMixer:
    """
    Mixes audio description narration with original video audio.

    Key features:
    - Audio ducking: Reduces original audio volume during descriptions
    - Crossfades: Smooth transitions in/out of descriptions
    - Zero dialogue interruption: Descriptions only in verified gaps
    """

    def __init__(
        self,
        ducking_level_db: float = -8.0,
        fade_duration_ms: int = 300,
    ):
        self.ducking_level = ducking_level_db
        self.fade_duration = fade_duration_ms

    async def extract_audio(self, video_path: str, output_path: str) -> str:
        """Extract audio track from video"""
        path = Path(video_path)
        if not path.exists():
            raise VideoProcessingError(f"Video file not found: {video_path}")

        try:
            cmd = [
                "ffmpeg",
                "-i", str(path),
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                "-y",
                output_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Extracted audio to {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            raise VideoProcessingError(
                f"Audio extraction failed: {e.stderr.decode()}"
            )

    async def mix_descriptions(
        self,
        original_video_path: str,
        description_segments: list[dict],
        output_path: str,
        ducking_level: Optional[float] = None,
    ) -> str:
        """
        Mix description audio segments with the original video.

        Args:
            original_video_path: Path to the original video
            description_segments: List of dicts with:
                - audio_path: Path to description audio file
                - start_time: When to insert (seconds)
                - duration: Duration of description (seconds)
            output_path: Path for the output file
            ducking_level: Override ducking level in dB

        Returns:
            Path to the output video with mixed audio
        """
        ducking = ducking_level or self.ducking_level

        if not description_segments:
            logger.warning("No description segments to mix")
            # Just copy the original
            import shutil
            shutil.copy2(original_video_path, output_path)
            return output_path

        try:
            # Build complex FFmpeg filter
            filter_parts = []
            inputs = ["-i", original_video_path]

            for i, seg in enumerate(description_segments):
                inputs.extend(["-i", seg["audio_path"]])

            # Create ducking filter for original audio
            # [0:a] is the original audio
            filter_complex = self._build_ducking_filter(
                description_segments, ducking, len(description_segments)
            )

            cmd = [
                "ffmpeg",
                *inputs,
                "-filter_complex", filter_complex,
                "-map", "0:v",
                "-map", "[final_audio]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-y",
                output_path,
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Mixed {len(description_segments)} descriptions into {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            raise VideoProcessingError(
                f"Audio mixing failed: {e.stderr.decode()}"
            )

    def _build_ducking_filter(
        self,
        segments: list[dict],
        ducking_db: float,
        num_inputs: int,
    ) -> str:
        """Build FFmpeg filter_complex string for ducking and mixing"""
        fade_s = self.fade_duration / 1000.0

        # Start with original audio, apply volume adjustments
        filters = []

        # Create volume envelope for ducking
        volume_points = []
        for seg in segments:
            start = seg["start_time"]
            duration = seg["duration"]
            # Fade down before description
            volume_points.append(f"volume=enable='between(t,{start-fade_s},{start+duration+fade_s})':volume={10**(ducking_db/20)}")

        # Apply ducking to original audio
        filters.append(f"[0:a]{''.join(f',{vp}' for vp in volume_points)}[ducked]")

        # Delay and mix each description
        for i in range(num_inputs):
            delay_ms = int(segments[i]["start_time"] * 1000)
            filters.append(
                f"[{i+1}:a]adelay={delay_ms}|{delay_ms},"
                f"afade=t=in:d={fade_s},afade=t=out:st={segments[i]['duration']-fade_s}:d={fade_s}"
                f"[desc_{i}]"
            )

        # Mix all together
        mix_inputs = "[ducked]" + "".join(f"[desc_{i}]" for i in range(num_inputs))
        filters.append(f"{mix_inputs}amix=inputs={num_inputs + 1}:duration=first[final_audio]")

        return ";".join(filters)

    async def create_description_audio_track(
        self,
        description_segments: list[dict],
        total_duration: float,
        output_path: str,
    ) -> str:
        """
        Create a standalone audio track with only descriptions.

        Useful for playing descriptions separately or as an audio-only file.
        """
        try:
            # Create silent base track
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"anullsrc=r=44100:cl=stereo:d={total_duration}",
            ]

            # Add each description
            for seg in description_segments:
                cmd.extend(["-i", seg["audio_path"]])

            # Build filter to mix descriptions onto silent track
            filter_parts = []
            for i, seg in enumerate(description_segments):
                delay_ms = int(seg["start_time"] * 1000)
                filter_parts.append(
                    f"[{i+1}:a]adelay={delay_ms}|{delay_ms}[d{i}]"
                )

            mix_inputs = "[0:a]" + "".join(f"[d{i}]" for i in range(len(description_segments)))
            filter_parts.append(
                f"{mix_inputs}amix=inputs={len(description_segments)+1}:duration=first[out]"
            )

            cmd.extend([
                "-filter_complex", ";".join(filter_parts),
                "-map", "[out]",
                "-c:a", "mp3",
                "-b:a", "192k",
                "-y",
                output_path,
            ])

            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Created description audio track: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            raise VideoProcessingError(
                f"Description audio track creation failed: {e.stderr.decode()}"
            )
