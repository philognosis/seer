"""
User Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a user"""

    email: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""

    id: UUID
    email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences"""

    # Voice settings
    primary_voice: Optional[str] = None
    backup_voice: Optional[str] = None
    voice_speed: Optional[float] = Field(None, ge=0.75, le=1.3)
    emotional_inflection: Optional[bool] = None

    # Description settings
    description_density: Optional[str] = None
    prioritize_emotions: Optional[int] = Field(None, ge=1, le=10)
    prioritize_actions: Optional[int] = Field(None, ge=1, le=10)
    prioritize_setting: Optional[int] = Field(None, ge=1, le=10)

    # Audio settings
    ducking_level: Optional[float] = Field(None, ge=-20.0, le=0.0)
    preserve_music: Optional[bool] = None

    # Accessibility
    keyboard_shortcuts_enabled: Optional[bool] = None
    audio_feedback_enabled: Optional[bool] = None
    high_contrast_mode: Optional[bool] = None

    # Learning
    learn_from_feedback: Optional[bool] = None
    save_watched_history: Optional[bool] = None


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response"""

    primary_voice: str = "female_us"
    backup_voice: str = "male_us"
    voice_speed: float = 1.0
    emotional_inflection: bool = True
    description_density: str = "standard"
    prioritize_emotions: int = 10
    prioritize_actions: int = 9
    prioritize_setting: int = 6
    ducking_level: float = -8.0
    preserve_music: bool = True
    keyboard_shortcuts_enabled: bool = True
    audio_feedback_enabled: bool = True
    high_contrast_mode: bool = True
    learn_from_feedback: bool = True
    save_watched_history: bool = True

    class Config:
        from_attributes = True
