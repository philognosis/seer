"""
Professional review system.
Manages the queue and process for professional audio description review.
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feedback import ProfessionalReview, ProfessionalReviewQueue

logger = logging.getLogger(__name__)


class ReviewSystem:
    """Professional review queue and management"""

    async def request_review(
        self,
        session: AsyncSession,
        video_id: UUID,
        requested_by: Optional[UUID] = None,
        reason: Optional[str] = None,
    ) -> ProfessionalReviewQueue:
        """Queue a video for professional review"""
        review_request = ProfessionalReviewQueue(
            video_id=video_id,
            requested_by=requested_by,
            reason=reason,
            status="pending",
        )
        session.add(review_request)
        await session.commit()

        logger.info(f"Professional review requested for video {video_id}")
        return review_request

    async def get_pending_reviews(
        self, session: AsyncSession
    ) -> list[ProfessionalReviewQueue]:
        """Get all pending review requests"""
        result = await session.execute(
            select(ProfessionalReviewQueue)
            .where(ProfessionalReviewQueue.status == "pending")
            .order_by(ProfessionalReviewQueue.created_at)
        )
        return list(result.scalars().all())

    async def submit_review(
        self,
        session: AsyncSession,
        video_id: UUID,
        reviewer_id: UUID,
        approved: bool,
        checklist: Optional[dict] = None,
        notes: Optional[str] = None,
    ) -> ProfessionalReview:
        """Submit a professional review"""
        review = ProfessionalReview(
            video_id=video_id,
            reviewer_id=reviewer_id,
            approved=approved,
            checklist=checklist or {},
            notes=notes,
        )
        session.add(review)

        # Update the review queue
        result = await session.execute(
            select(ProfessionalReviewQueue).where(
                ProfessionalReviewQueue.video_id == video_id,
                ProfessionalReviewQueue.status.in_(["pending", "in_progress"]),
            )
        )
        queue_item = result.scalar_one_or_none()
        if queue_item:
            queue_item.status = "completed"
            queue_item.completed_at = datetime.utcnow()

        await session.commit()

        logger.info(
            f"Professional review submitted for video {video_id}: "
            f"{'approved' if approved else 'not approved'}"
        )
        return review
