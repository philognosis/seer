"""
User preference engine.
Manages user settings and learns from feedback.
"""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserPreference

logger = logging.getLogger(__name__)


class PreferenceEngine:
    """Manages user preferences and learning"""

    DEFAULT_PREFERENCES = {
        "primary_voice": "female_us",
        "backup_voice": "male_us",
        "voice_speed": 1.0,
        "emotional_inflection": True,
        "description_density": "standard",
        "prioritize_emotions": 10,
        "prioritize_actions": 9,
        "prioritize_setting": 6,
        "ducking_level": -8.0,
        "preserve_music": True,
        "keyboard_shortcuts_enabled": True,
        "audio_feedback_enabled": True,
        "high_contrast_mode": True,
        "learn_from_feedback": True,
        "save_watched_history": True,
    }

    async def get_preferences(
        self, session: AsyncSession, user_id: UUID
    ) -> dict:
        """Get user preferences or defaults"""
        result = await session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        pref = result.scalar_one_or_none()

        if pref is None:
            return self.DEFAULT_PREFERENCES.copy()

        return {
            key: getattr(pref, key, default)
            for key, default in self.DEFAULT_PREFERENCES.items()
        }

    async def update_preferences(
        self,
        session: AsyncSession,
        user_id: UUID,
        updates: dict,
    ) -> dict:
        """Update user preferences"""
        result = await session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        pref = result.scalar_one_or_none()

        if pref is None:
            pref = UserPreference(user_id=user_id, **updates)
            session.add(pref)
        else:
            for key, value in updates.items():
                if hasattr(pref, key):
                    setattr(pref, key, value)

        await session.commit()
        return await self.get_preferences(session, user_id)

    async def learn_from_feedback(
        self,
        session: AsyncSession,
        user_id: UUID,
        feedback: dict,
    ) -> None:
        """Adjust preferences based on user feedback"""
        prefs = await self.get_preferences(session, user_id)

        if not prefs.get("learn_from_feedback", True):
            return

        updates = {}

        # If user reports too much detail, reduce density
        if feedback.get("too_much_detail"):
            current = prefs["description_density"]
            if current == "detailed":
                updates["description_density"] = "standard"
            elif current == "standard":
                updates["description_density"] = "minimal"

        # If user reports too little detail, increase density
        if feedback.get("too_little_detail"):
            current = prefs["description_density"]
            if current == "minimal":
                updates["description_density"] = "standard"
            elif current == "standard":
                updates["description_density"] = "detailed"

        if updates:
            await self.update_preferences(session, user_id, updates)
            logger.info(f"Adjusted preferences for user {user_id}: {updates}")
