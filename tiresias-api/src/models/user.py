"""
User ORM models
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    preference = relationship(
        "UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    feedback = relationship("Feedback", back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    # Voice settings
    primary_voice: Mapped[str] = mapped_column(String(50), default="female_us")
    backup_voice: Mapped[str] = mapped_column(String(50), default="male_us")
    voice_speed: Mapped[float] = mapped_column(Float, default=1.0)
    emotional_inflection: Mapped[bool] = mapped_column(Boolean, default=True)

    # Description settings
    description_density: Mapped[str] = mapped_column(String(50), default="standard")
    prioritize_emotions: Mapped[int] = mapped_column(Integer, default=10)
    prioritize_actions: Mapped[int] = mapped_column(Integer, default=9)
    prioritize_setting: Mapped[int] = mapped_column(Integer, default=6)

    # Audio settings
    ducking_level: Mapped[float] = mapped_column(Float, default=-8.0)
    preserve_music: Mapped[bool] = mapped_column(Boolean, default=True)

    # Accessibility
    keyboard_shortcuts_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    audio_feedback_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    high_contrast_mode: Mapped[bool] = mapped_column(Boolean, default=True)

    # Learning
    learn_from_feedback: Mapped[bool] = mapped_column(Boolean, default=True)
    save_watched_history: Mapped[bool] = mapped_column(Boolean, default=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="preference")
