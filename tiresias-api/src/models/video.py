"""
Video ORM models
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # Source
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Processing
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="queued", index=True
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Settings used
    llm_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    voice: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description_density: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # File paths
    original_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_audio_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Quality metrics
    dialogue_interruptions: Mapped[int] = mapped_column(Integer, default=0)
    descriptions_count: Mapped[int] = mapped_column(Integer, default=0)
    average_gap_duration: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Community
    professionally_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    community_rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="videos")
    descriptions = relationship(
        "Description", back_populates="video", cascade="all, delete-orphan"
    )
    feedback = relationship(
        "Feedback", back_populates="video", cascade="all, delete-orphan"
    )
    community_descriptions = relationship(
        "CommunityDescription", back_populates="video", cascade="all, delete-orphan"
    )
