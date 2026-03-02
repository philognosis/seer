"""
TTS voice endpoints
"""
from fastapi import APIRouter

from src.schemas.response import VoiceInfo

router = APIRouter(prefix="/voices", tags=["Voices"])

# Available voices
VOICES = [
    VoiceInfo(
        id="female_us",
        name="Sarah",
        accent="US English",
        gender="Female",
        provider="elevenlabs",
        sample_url=None,
    ),
    VoiceInfo(
        id="male_us",
        name="James",
        accent="US English",
        gender="Male",
        provider="elevenlabs",
        sample_url=None,
    ),
    VoiceInfo(
        id="female_uk",
        name="Emma",
        accent="UK English",
        gender="Female",
        provider="elevenlabs",
        sample_url=None,
    ),
    VoiceInfo(
        id="male_uk",
        name="William",
        accent="UK English",
        gender="Male",
        provider="elevenlabs",
        sample_url=None,
    ),
]


@router.get("/", response_model=list[VoiceInfo])
async def list_voices() -> list[VoiceInfo]:
    """
    List available TTS voices.

    Accessibility: Returns available voice options with accent and gender
    information to help users choose their preferred narration voice.
    """
    return VOICES


@router.get("/{voice_id}", response_model=VoiceInfo)
async def get_voice(voice_id: str) -> VoiceInfo:
    """
    Get details for a specific voice.

    Accessibility: Returns detailed information about a specific voice option.
    """
    for voice in VOICES:
        if voice.id == voice_id:
            return voice

    from src.core.exceptions import ResourceNotFoundError

    raise ResourceNotFoundError("Voice", voice_id)
