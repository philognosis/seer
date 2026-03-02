"""
General utility functions
"""
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_timestamp(seconds: float) -> str:
    """Format seconds into MM:SS.ms timestamp"""
    minutes = int(seconds // 60)
    remaining = seconds % 60
    return f"{minutes:02d}:{remaining:05.2f}"


def file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def ensure_dir(path: str | Path) -> Path:
    """Ensure a directory exists, creating it if necessary"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    return Path(file_path).stat().st_size / (1024 * 1024)
