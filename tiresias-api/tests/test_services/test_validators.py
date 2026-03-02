"""
Tests for validation utilities
"""
from src.utils.validators import (
    sanitize_filename,
    validate_density,
    validate_llm_provider,
    validate_video_file,
    validate_video_url,
    validate_voice_id,
)


def test_validate_youtube_url():
    """Test YouTube URL validation"""
    assert validate_video_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "youtube"
    assert validate_video_url("https://youtu.be/dQw4w9WgXcQ") == "youtube"


def test_validate_vimeo_url():
    """Test Vimeo URL validation"""
    assert validate_video_url("https://vimeo.com/123456789") == "vimeo"


def test_validate_dailymotion_url():
    """Test Dailymotion URL validation"""
    assert validate_video_url("https://www.dailymotion.com/video/x8abc") == "dailymotion"


def test_validate_invalid_url():
    """Test invalid URL validation"""
    assert validate_video_url("https://example.com/video") is None
    assert validate_video_url("not-a-url") is None


def test_validate_video_file():
    """Test video file validation"""
    assert validate_video_file("video.mp4") is True
    assert validate_video_file("video.mov") is True
    assert validate_video_file("video.avi") is True
    assert validate_video_file("video.webm") is True
    assert validate_video_file("document.pdf") is False
    assert validate_video_file("image.jpg") is False


def test_validate_voice_id():
    """Test voice ID validation"""
    assert validate_voice_id("female_us") is True
    assert validate_voice_id("male_uk") is True
    assert validate_voice_id("invalid_voice") is False


def test_validate_llm_provider():
    """Test LLM provider validation"""
    assert validate_llm_provider("gemini") is True
    assert validate_llm_provider("claude") is True
    assert validate_llm_provider("openai") is True
    assert validate_llm_provider("invalid") is False


def test_validate_density():
    """Test density validation"""
    assert validate_density("minimal") is True
    assert validate_density("standard") is True
    assert validate_density("detailed") is True
    assert validate_density("invalid") is False


def test_sanitize_filename():
    """Test filename sanitization"""
    assert sanitize_filename("normal.mp4") == "normal.mp4"
    assert sanitize_filename("../../../etc/passwd") == "etcpasswd"
    assert sanitize_filename('.hidden.mp4') == "hidden.mp4"
    assert sanitize_filename('file<>:"/\\|?*.mp4') == "file.mp4"
