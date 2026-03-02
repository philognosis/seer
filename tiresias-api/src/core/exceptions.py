"""
Custom exceptions for Tiresias
"""
from typing import Any, Optional


class TiresiasException(Exception):
    """Base exception for Tiresias"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class VideoDownloadError(TiresiasException):
    """Video download failed"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="VIDEO_DOWNLOAD_ERROR",
            status_code=400,
            details=details,
        )


class VideoProcessingError(TiresiasException):
    """Video processing failed"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="VIDEO_PROCESSING_ERROR",
            status_code=500,
            details=details,
        )


class LLMProviderError(TiresiasException):
    """LLM provider error"""

    def __init__(self, message: str, provider: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=f"LLM_PROVIDER_ERROR_{provider.upper()}",
            status_code=502,
            details=details,
        )


class TTSProviderError(TiresiasException):
    """TTS provider error"""

    def __init__(self, message: str, provider: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=f"TTS_PROVIDER_ERROR_{provider.upper()}",
            status_code=502,
            details=details,
        )


class ValidationError(TiresiasException):
    """Input validation error"""

    def __init__(self, message: str, field: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details={"field": field, **(details or {})},
        )


class ResourceNotFoundError(TiresiasException):
    """Requested resource not found"""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID {resource_id} not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )
