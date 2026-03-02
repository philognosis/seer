"""
Feedback ORM models
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # Ratings (1-5)
    accuracy_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timing_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    helpfulness_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    conciseness_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Issues
    interrupted_dialogue: Mapped[bool] = mapped_column(Boolean, default=False)
    missed_critical_visual: Mapped[bool] = mapped_column(Boolean, default=False)
    too_much_detail: Mapped[bool] = mapped_column(Boolean, default=False)
    too_little_detail: Mapped[bool] = mapped_column(Boolean, default=False)
    wrong_character: Mapped[bool] = mapped_column(Boolean, default=False)
    timing_off: Mapped[bool] = mapped_column(Boolean, default=False)

    # Details
    timestamp: Mapped[float | None] = mapped_column(Float, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    video = relationship("Video", back_populates="feedback")
    user = relationship("User", back_populates="feedback")


class ProfessionalReviewQueue(Base):
    __tablename__ = "professional_review_queue"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    requested_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, default="pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ProfessionalReview(Base):
    __tablename__ = "professional_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    checklist: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
