"""
Video processing endpoints
"""
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from fastapi.responses import FileResponse

from src.core.exceptions import ResourceNotFoundError, ValidationError
from src.core.settings import get_settings
from src.schemas.video import (
    VideoFromURLRequest,
    VideoListResponse,
    VideoProcessingOptions,
    VideoStatusResponse,
    VideoUploadResponse,
)
from src.services.video.downloader import VideoDownloader

router = APIRouter(prefix="/videos", tags=["Videos"])
settings = get_settings()


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(..., description="Video file to process"),
    voice: str = Form("female_us", description="TTS voice to use"),
    llm_provider: str = Form("gemini", description="LLM provider to use"),
    description_density: str = Form("standard", description="Description density"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> VideoUploadResponse:
    """
    Upload a video file for processing.

    Accessibility: This endpoint accepts video files and queues them for
    audio description generation. Progress updates are available via WebSocket
    or status polling endpoint.
    """
    # Validate file size
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"File size {file.size} exceeds maximum {settings.MAX_UPLOAD_SIZE}",
            field="file",
        )

    # Validate file type
    allowed_types = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"]
    if file.content_type not in allowed_types:
        raise ValidationError(
            f"File type {file.content_type} not supported",
            field="file",
        )

    # Generate unique ID
    video_id = str(uuid.uuid4())

    # Save uploaded file
    upload_path = Path(settings.UPLOAD_DIR) / f"{video_id}_{file.filename}"
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Queue processing task (will be handled by Celery in production)
    processing_options = VideoProcessingOptions(
        voice=voice,
        llm_provider=llm_provider,
        description_density=description_density,
    )

    # In production, this would call: process_video_task.delay(...)
    background_tasks.add_task(
        _placeholder_process,
        video_id=video_id,
        video_path=str(upload_path),
        options=processing_options.model_dump(),
    )

    return VideoUploadResponse(
        video_id=video_id,
        status="queued",
        message="Video uploaded successfully. Processing started.",
    )


@router.post("/from-url", response_model=VideoUploadResponse)
async def process_from_url(
    request: VideoFromURLRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> VideoUploadResponse:
    """
    Process a video from URL (YouTube, Vimeo, Dailymotion, etc.).

    Accessibility: This endpoint downloads and processes videos from
    supported platforms. Progress updates available via status endpoint.
    """
    video_id = str(uuid.uuid4())

    # Validate URL
    downloader = VideoDownloader()
    if not downloader.is_supported_url(request.url):
        raise ValidationError(
            "URL not supported. Supported platforms: YouTube, Vimeo, Dailymotion",
            field="url",
        )

    # Queue processing task
    background_tasks.add_task(
        _placeholder_process,
        video_id=video_id,
        url=request.url,
        options=request.options.model_dump(),
    )

    return VideoUploadResponse(
        video_id=video_id,
        status="queued",
        message="Video download and processing started.",
    )


@router.get("/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(video_id: str) -> VideoStatusResponse:
    """
    Get processing status of a video.

    Accessibility: This endpoint provides detailed progress information
    suitable for screen reader announcements.
    """
    # TODO: Query database/cache for actual status
    return VideoStatusResponse(
        video_id=video_id,
        status="processing",
        progress=45,
        current_step="Generating descriptions",
        estimated_time_remaining=300,
        error=None,
    )


@router.get("/{video_id}/descriptions")
async def get_video_descriptions(video_id: str) -> dict:
    """
    Get generated descriptions for a video.

    Accessibility: Returns all audio descriptions with timestamps.
    """
    # TODO: Query database for descriptions
    return {
        "video_id": video_id,
        "descriptions": [],
        "total": 0,
    }


@router.get("/{video_id}/download")
async def download_video(video_id: str, track: str = "combined") -> FileResponse:
    """
    Download processed video or audio track.

    Args:
        track: 'combined' (video with descriptions), 'description_only' (audio track),
               or 'transcript' (text file)

    Accessibility: This endpoint provides the final output in various formats.
    """
    output_path = Path(settings.OUTPUT_DIR) / video_id

    if track == "combined":
        file_path = output_path / "final_video.mp4"
    elif track == "description_only":
        file_path = output_path / "descriptions.mp3"
    elif track == "transcript":
        file_path = output_path / "transcript.txt"
    else:
        raise ValidationError("Invalid track type", field="track")

    if not file_path.exists():
        raise ResourceNotFoundError("Video", video_id)

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
    )


@router.delete("/{video_id}")
async def delete_video(video_id: str) -> dict:
    """
    Delete a processed video and all associated files.

    Accessibility: Cleanup endpoint for user privacy.
    """
    output_path = Path(settings.OUTPUT_DIR) / video_id
    upload_path = Path(settings.UPLOAD_DIR)

    if output_path.exists():
        shutil.rmtree(output_path)

    for file in upload_path.glob(f"{video_id}_*"):
        file.unlink()

    return {"message": "Video deleted successfully"}


async def _placeholder_process(**kwargs: object) -> None:
    """Placeholder for video processing task (replaced by Celery in production)"""
    pass
