"""
Main API v1 router
"""
from fastapi import APIRouter

from src.api.v1.videos import router as videos_router
from src.api.v1.users import router as users_router
from src.api.v1.models import router as models_router
from src.api.v1.voices import router as voices_router
from src.api.v1.community import router as community_router

api_router = APIRouter()

api_router.include_router(videos_router)
api_router.include_router(users_router)
api_router.include_router(models_router)
api_router.include_router(voices_router)
api_router.include_router(community_router)
