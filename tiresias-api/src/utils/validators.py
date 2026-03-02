"""
Input validation utilities
"""
import re
from pathlib import Path
from typing import Optional

SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".aac", ".ogg", ".flac"}

URL_PATTERNS = {
    "youtube": re.compile(
        r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+"
    ),
    "vimeo": re.compile(r"^(https?://)?(www\.)?vimeo\.com/\d+"),
    "dailymotion": re.compile(
        r"^(https?://)?(www\.)?dailymotion\.com/video/[\w]+"
    ),
}


def validate_video_url(url: str) -> Optional[str]:
    """
    Validate a video URL and return the platform name.

    Returns platform name if valid, None if not.
    """
    for platform, pattern in URL_PATTERNS.items():
        if pattern.match(url):
            return platform
    return None


def validate_video_file(filename: str) -> bool:
    """Check if a filename has a supported video extension"""
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_VIDEO_EXTENSIONS


def validate_voice_id(voice_id: str) -> bool:
    """Check if a voice ID is valid"""
    valid_voices = {"female_us", "male_us", "female_uk", "male_uk"}
    return voice_id in valid_voices


def validate_llm_provider(provider: str) -> bool:
    """Check if an LLM provider is valid"""
    valid_providers = {"gemini", "claude", "openai"}
    return provider in valid_providers


def validate_density(density: str) -> bool:
    """Check if a description density value is valid"""
    valid_densities = {"minimal", "standard", "detailed"}
    return density in valid_densities


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal"""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Remove leading dots (hidden files)
    filename = filename.lstrip(".")
    # Truncate to reasonable length
    name = Path(filename)
    return f"{name.stem[:200]}{name.suffix}"
