"""
FastAPI dependencies
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as a FastAPI dependency"""
    async for session in get_db():
        yield session
