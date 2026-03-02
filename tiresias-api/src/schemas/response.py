"""
API response schemas
"""
from typing import Any, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response wrapper"""

    success: bool = True
    message: str = ""
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response"""

    error: str
    message: str
    details: Optional[Any] = None


class FeedbackCreate(BaseModel):
    """Schema for submitting feedback"""

    video_id: str

    # Ratings (1-5)
    accuracy_rating: Optional[int] = None
    timing_rating: Optional[int] = None
    helpfulness_rating: Optional[int] = None
    conciseness_rating: Optional[int] = None

    # Issues
    interrupted_dialogue: bool = False
    missed_critical_visual: bool = False
    too_much_detail: bool = False
    too_little_detail: bool = False
    wrong_character: bool = False
    timing_off: bool = False

    # Details
    timestamp: Optional[float] = None
    comments: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response"""

    id: str
    video_id: str
    message: str = "Feedback submitted successfully"


class LLMProviderInfo(BaseModel):
    """LLM provider information"""

    id: str
    name: str
    description: str
    requires_api_key: bool
    is_available: bool
    model_name: str
    capabilities: list[str]


class VoiceInfo(BaseModel):
    """TTS voice information"""

    id: str
    name: str
    accent: str
    gender: str
    provider: str
    sample_url: Optional[str] = None


class ProfessionalReviewRequest(BaseModel):
    """Request for professional review"""

    video_id: str
    reason: Optional[str] = None
