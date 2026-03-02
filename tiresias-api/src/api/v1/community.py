"""
Community features endpoints
"""
import uuid

from fastapi import APIRouter

from src.schemas.description import (
    CommunityDescriptionCreate,
    CommunityDescriptionResponse,
    VoteRequest,
)
from src.schemas.response import (
    FeedbackCreate,
    FeedbackResponse,
    ProfessionalReviewRequest,
)

router = APIRouter(prefix="/community", tags=["Community"])


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackCreate) -> FeedbackResponse:
    """
    Submit feedback on a video's audio descriptions.

    Accessibility: Allows users to rate and report issues with
    generated descriptions including timing, accuracy, and detail level.
    """
    feedback_id = str(uuid.uuid4())
    # TODO: Save to database
    return FeedbackResponse(
        id=feedback_id,
        video_id=feedback.video_id,
        message="Feedback submitted successfully. Thank you for helping improve Tiresias!",
    )


@router.post("/descriptions", response_model=CommunityDescriptionResponse)
async def submit_community_description(
    description: CommunityDescriptionCreate,
) -> dict:
    """
    Submit an alternative description for a video moment.

    Accessibility: Allows community members to contribute
    better descriptions for specific moments in videos.
    """
    desc_id = str(uuid.uuid4())
    # TODO: Save to database
    return {
        "id": desc_id,
        "video_id": str(description.video_id),
        "timestamp": description.timestamp,
        "text": description.text,
        "upvotes": 0,
        "downvotes": 0,
        "reviewed_by_professional": False,
        "is_approved": False,
        "created_at": "2026-01-01T00:00:00Z",
    }


@router.get("/descriptions/{video_id}")
async def get_community_descriptions(video_id: str) -> dict:
    """
    Get community-submitted descriptions for a video.

    Accessibility: Returns all community-contributed alternative
    descriptions for a specific video.
    """
    # TODO: Query from database
    return {
        "video_id": video_id,
        "descriptions": [],
        "total": 0,
    }


@router.post("/descriptions/{description_id}/vote")
async def vote_on_description(
    description_id: str,
    vote: VoteRequest,
) -> dict:
    """
    Vote on a community description.

    Accessibility: Allows users to upvote or downvote community
    descriptions to surface the best alternatives.
    """
    # TODO: Save vote to database
    return {
        "description_id": description_id,
        "vote": vote.vote,
        "message": "Vote recorded successfully",
    }


@router.post("/review-request")
async def request_professional_review(
    request: ProfessionalReviewRequest,
) -> dict:
    """
    Request a professional review for a video's descriptions.

    Accessibility: Queues a video for review by a certified
    audio description professional.
    """
    review_id = str(uuid.uuid4())
    # TODO: Save to database
    return {
        "review_id": review_id,
        "video_id": request.video_id,
        "status": "pending",
        "message": "Professional review requested. You will be notified when complete.",
    }


@router.get("/approved")
async def get_approved_videos(
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """
    Get professionally approved videos.

    Accessibility: Returns videos that have been reviewed and
    approved by professional audio describers.
    """
    # TODO: Query from database
    return {
        "videos": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
    }
