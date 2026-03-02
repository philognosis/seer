"""
Video downloader service using yt-dlp
"""
import logging
import re
from pathlib import Path
from typing import Optional

import yt_dlp

from src.core.exceptions import VideoDownloadError
from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Supported URL patterns
SUPPORTED_PATTERNS = [
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
    r"(https?://)?(www\.)?vimeo\.com/",
    r"(https?://)?(www\.)?dailymotion\.com/",
]


class VideoDownloader:
    """Downloads videos from supported platforms using yt-dlp"""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or settings.UPLOAD_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is from a supported platform"""
        return any(re.search(pattern, url) for pattern in SUPPORTED_PATTERNS)

    def get_platform(self, url: str) -> str:
        """Identify the platform from URL"""
        if re.search(r"youtube\.com|youtu\.be", url):
            return "youtube"
        elif re.search(r"vimeo\.com", url):
            return "vimeo"
        elif re.search(r"dailymotion\.com", url):
            return "dailymotion"
        return "unknown"

    async def download(
        self,
        url: str,
        video_id: str,
        progress_callback: Optional[callable] = None,
    ) -> dict:
        """
        Download a video from URL.

        Returns dict with:
            - path: Path to downloaded file
            - title: Video title
            - duration: Video duration in seconds
            - resolution: Video resolution
            - fps: Frames per second
        """
        if not self.is_supported_url(url):
            raise VideoDownloadError(f"Unsupported URL: {url}")

        output_template = str(self.output_dir / f"{video_id}_%(title)s.%(ext)s")

        ydl_opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "outtmpl": output_template,
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        if progress_callback:

            def hook(d: dict) -> None:
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                    downloaded = d.get("downloaded_bytes", 0)
                    if total > 0:
                        progress_callback(int(downloaded / total * 100))

            ydl_opts["progress_hooks"] = [hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                if info is None:
                    raise VideoDownloadError("Failed to extract video info")

                # Find the downloaded file
                filename = ydl.prepare_filename(info)
                # yt-dlp may change extension to mp4
                file_path = Path(filename)
                if not file_path.exists():
                    file_path = file_path.with_suffix(".mp4")

                if not file_path.exists():
                    # Search for any file matching the video_id
                    matches = list(self.output_dir.glob(f"{video_id}_*"))
                    if matches:
                        file_path = matches[0]
                    else:
                        raise VideoDownloadError("Downloaded file not found")

                return {
                    "path": str(file_path),
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "resolution": f"{info.get('width', 0)}x{info.get('height', 0)}",
                    "fps": info.get("fps", 30),
                }

        except yt_dlp.utils.DownloadError as e:
            raise VideoDownloadError(
                f"Failed to download video: {e}",
                details={"url": url, "platform": self.get_platform(url)},
            )

    async def get_video_info(self, url: str) -> dict:
        """Get video metadata without downloading"""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info is None:
                    raise VideoDownloadError("Failed to extract video info")

                return {
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "resolution": f"{info.get('width', 0)}x{info.get('height', 0)}",
                    "fps": info.get("fps", 30),
                    "thumbnail": info.get("thumbnail"),
                    "description": info.get("description", ""),
                }

        except yt_dlp.utils.DownloadError as e:
            raise VideoDownloadError(f"Failed to get video info: {e}")
