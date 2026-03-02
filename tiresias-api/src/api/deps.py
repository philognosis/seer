"""
Route-level dependencies
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency for routes"""
    async for session in get_db():
        yield session
