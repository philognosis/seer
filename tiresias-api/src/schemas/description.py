"""
Description Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DescriptionResponse(BaseModel):
    """Schema for a single description"""

    id: UUID
    timestamp: float
    duration: float
    text: str
    priority: Optional[int] = None
    scene_type: Optional[str] = None
    ai_confidence: Optional[float] = None

    class Config:
        from_attributes = True


class DescriptionListResponse(BaseModel):
    """Schema for list of descriptions"""

    video_id: str
    descriptions: list[DescriptionResponse]
    total: int


class CommunityDescriptionCreate(BaseModel):
    """Schema for submitting a community description"""

    video_id: UUID
    timestamp: float = Field(..., ge=0.0)
    text: str = Field(..., min_length=1, max_length=500)


class CommunityDescriptionResponse(BaseModel):
    """Schema for community description response"""

    id: UUID
    video_id: UUID
    contributor_id: Optional[UUID] = None
    timestamp: float
    text: str
    upvotes: int = 0
    downvotes: int = 0
    reviewed_by_professional: bool = False
    is_approved: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class VoteRequest(BaseModel):
    """Schema for voting on a community description"""

    vote: int = Field(..., ge=-1, le=1, description="Vote: -1 for downvote, 1 for upvote")
