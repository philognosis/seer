"""
Community quality and feedback system.
Manages ratings, alternative descriptions, and voting.
"""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.description import CommunityDescription, DescriptionVote
from src.models.feedback import Feedback

logger = logging.getLogger(__name__)


class QualitySystem:
    """Community-driven quality management"""

    async def submit_feedback(
        self,
        session: AsyncSession,
        video_id: UUID,
        user_id: Optional[UUID],
        feedback_data: dict,
    ) -> Feedback:
        """Submit feedback on a video's descriptions"""
        feedback = Feedback(
            video_id=video_id,
            user_id=user_id,
            **feedback_data,
        )
        session.add(feedback)
        await session.commit()

        logger.info(f"Feedback submitted for video {video_id}")
        return feedback

    async def get_video_ratings(
        self, session: AsyncSession, video_id: UUID
    ) -> dict:
        """Get aggregate ratings for a video"""
        result = await session.execute(
            select(
                func.avg(Feedback.accuracy_rating).label("avg_accuracy"),
                func.avg(Feedback.timing_rating).label("avg_timing"),
                func.avg(Feedback.helpfulness_rating).label("avg_helpfulness"),
                func.avg(Feedback.conciseness_rating).label("avg_conciseness"),
                func.count(Feedback.id).label("total_feedback"),
            ).where(Feedback.video_id == video_id)
        )

        row = result.one()
        return {
            "accuracy": float(row.avg_accuracy) if row.avg_accuracy else None,
            "timing": float(row.avg_timing) if row.avg_timing else None,
            "helpfulness": float(row.avg_helpfulness) if row.avg_helpfulness else None,
            "conciseness": float(row.avg_conciseness) if row.avg_conciseness else None,
            "total_feedback": row.total_feedback,
        }

    async def submit_community_description(
        self,
        session: AsyncSession,
        video_id: UUID,
        contributor_id: Optional[UUID],
        timestamp: float,
        text: str,
    ) -> CommunityDescription:
        """Submit an alternative community description"""
        desc = CommunityDescription(
            video_id=video_id,
            contributor_id=contributor_id,
            timestamp=timestamp,
            text=text,
        )
        session.add(desc)
        await session.commit()

        logger.info(f"Community description submitted for video {video_id} at {timestamp}s")
        return desc

    async def vote_on_description(
        self,
        session: AsyncSession,
        description_id: UUID,
        user_id: UUID,
        vote: int,
    ) -> None:
        """Vote on a community description (+1 or -1)"""
        # Check for existing vote
        result = await session.execute(
            select(DescriptionVote).where(
                DescriptionVote.description_id == description_id,
                DescriptionVote.user_id == user_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.vote = vote
        else:
            session.add(
                DescriptionVote(
                    description_id=description_id,
                    user_id=user_id,
                    vote=vote,
                )
            )

        # Update vote counts on the description
        desc_result = await session.execute(
            select(CommunityDescription).where(
                CommunityDescription.id == description_id
            )
        )
        desc = desc_result.scalar_one_or_none()
        if desc:
            # Recalculate votes
            votes_result = await session.execute(
                select(
                    func.sum(
                        func.case((DescriptionVote.vote == 1, 1), else_=0)
                    ).label("upvotes"),
                    func.sum(
                        func.case((DescriptionVote.vote == -1, 1), else_=0)
                    ).label("downvotes"),
                ).where(DescriptionVote.description_id == description_id)
            )
            votes = votes_result.one()
            desc.upvotes = votes.upvotes or 0
            desc.downvotes = votes.downvotes or 0

        await session.commit()
