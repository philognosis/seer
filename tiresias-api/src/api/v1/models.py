"""
LLM provider endpoints
"""
from fastapi import APIRouter

from src.core.settings import get_settings
from src.schemas.response import LLMProviderInfo

router = APIRouter(prefix="/models", tags=["LLM Providers"])
settings = get_settings()

# Available LLM providers
LLM_PROVIDERS = [
    LLMProviderInfo(
        id="gemini",
        name="Google Gemini 2.0 Flash",
        description="Fast, capable multi-modal model. Free tier available.",
        requires_api_key=True,
        is_available=True,
        model_name="gemini-2.0-flash",
        capabilities=["vision", "text", "video"],
    ),
    LLMProviderInfo(
        id="claude",
        name="Anthropic Claude 3.5 Sonnet",
        description="Excellent at nuanced descriptions and narrative understanding.",
        requires_api_key=True,
        is_available=True,
        model_name="claude-3-5-sonnet-20241022",
        capabilities=["vision", "text"],
    ),
    LLMProviderInfo(
        id="openai",
        name="OpenAI GPT-4 Vision",
        description="Strong visual understanding and description generation.",
        requires_api_key=True,
        is_available=True,
        model_name="gpt-4o",
        capabilities=["vision", "text"],
    ),
]


@router.get("/", response_model=list[LLMProviderInfo])
async def list_providers() -> list[LLMProviderInfo]:
    """
    List available LLM providers.

    Accessibility: Returns available AI models for description generation
    with their capabilities and requirements.
    """
    providers = []
    for provider in LLM_PROVIDERS:
        p = provider.model_copy()
        # Check if API key is configured
        if provider.id == "gemini":
            p.is_available = bool(settings.GEMINI_API_KEY)
        elif provider.id == "claude":
            p.is_available = bool(settings.ANTHROPIC_API_KEY)
        elif provider.id == "openai":
            p.is_available = bool(settings.OPENAI_API_KEY)
        providers.append(p)
    return providers


@router.get("/{provider_id}", response_model=LLMProviderInfo)
async def get_provider(provider_id: str) -> LLMProviderInfo:
    """
    Get details for a specific LLM provider.

    Accessibility: Returns detailed information about a specific AI model.
    """
    for provider in LLM_PROVIDERS:
        if provider.id == provider_id:
            return provider

    from src.core.exceptions import ResourceNotFoundError

    raise ResourceNotFoundError("LLM Provider", provider_id)


@router.get("/default")
async def get_default_provider() -> dict:
    """
    Get the default LLM provider.

    Accessibility: Returns the currently configured default AI model.
    """
    return {"default_provider": settings.DEFAULT_LLM_PROVIDER}
