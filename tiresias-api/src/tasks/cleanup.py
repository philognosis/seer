"""
Cleanup tasks for temporary files and old data.
"""
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from src.core.settings import get_settings
from src.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="cleanup_temp_files")
def cleanup_temp_files(max_age_hours: int = 24) -> dict:
    """
    Clean up temporary files older than max_age_hours.

    Runs periodically to prevent disk space exhaustion.
    """
    temp_dir = Path(settings.TEMP_DIR)
    if not temp_dir.exists():
        return {"cleaned": 0, "errors": 0}

    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    cleaned = 0
    errors = 0

    for item in temp_dir.iterdir():
        try:
            if item.is_dir():
                # Check modification time
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime < cutoff:
                    shutil.rmtree(item)
                    cleaned += 1
                    logger.info(f"Cleaned up temp directory: {item}")
        except Exception as e:
            errors += 1
            logger.error(f"Failed to clean up {item}: {e}")

    return {"cleaned": cleaned, "errors": errors}


@celery_app.task(name="cleanup_old_uploads")
def cleanup_old_uploads(max_age_hours: int = 72) -> dict:
    """Clean up old upload files that have been processed"""
    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.exists():
        return {"cleaned": 0, "errors": 0}

    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    cleaned = 0
    errors = 0

    for item in upload_dir.iterdir():
        try:
            if item.is_file():
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime < cutoff:
                    item.unlink()
                    cleaned += 1
                    logger.info(f"Cleaned up upload: {item}")
        except Exception as e:
            errors += 1
            logger.error(f"Failed to clean up {item}: {e}")

    return {"cleaned": cleaned, "errors": errors}
