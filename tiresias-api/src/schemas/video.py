"""
Video Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class VideoProcessingOptions(BaseModel):
    """Options for video processing"""

    voice: str = Field(default="female_us", description="TTS voice to use")
    llm_provider: str = Field(default="gemini", description="LLM provider")
    description_density: str = Field(default="standard", description="Description density")
    ducking_level: float = Field(default=-8.0, description="Audio ducking level in dB")
    emotional_inflection: bool = Field(default=True, description="Enable emotional inflection")
    voice_speed: float = Field(default=1.0, ge=0.75, le=1.3, description="Voice speed multiplier")


class VideoFromURLRequest(BaseModel):
    """Request to process a video from URL"""

    url: str = Field(..., description="Video URL (YouTube, Vimeo, Dailymotion)")
    options: VideoProcessingOptions = Field(default_factory=VideoProcessingOptions)


class VideoUploadResponse(BaseModel):
    """Response after video upload/URL submission"""

    video_id: str
    status: str
    message: str


class VideoStatusResponse(BaseModel):
    """Video processing status response"""

    video_id: str
    status: str  # queued, downloading, analyzing, transcribing, generating, mixing, completed, failed
    progress: int = Field(ge=0, le=100)
    current_step: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds
    error: Optional[str] = None


class VideoMetadata(BaseModel):
    """Video metadata"""

    id: UUID
    title: Optional[str] = None
    duration: Optional[float] = None
    resolution: Optional[str] = None
    fps: Optional[float] = None
    source_type: str
    source_url: Optional[str] = None
    status: str
    progress: int
    descriptions_count: int = 0
    dialogue_interruptions: int = 0
    community_rating: Optional[float] = None
    professionally_approved: bool = False
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """Response for listing videos"""

    videos: list[VideoMetadata]
    total: int
    page: int
    page_size: int
