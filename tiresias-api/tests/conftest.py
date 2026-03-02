"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def sample_video_options():
    """Sample video processing options"""
    return {
        "voice": "female_us",
        "llm_provider": "gemini",
        "description_density": "standard",
    }
