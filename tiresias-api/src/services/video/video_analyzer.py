"""
Video analysis service using LLM vision capabilities
"""
import base64
import logging
from pathlib import Path
from typing import Optional

from src.core.exceptions import VideoProcessingError
from src.services.llm.provider_base import LLMProvider

logger = logging.getLogger(__name__)

FRAME_ANALYSIS_PROMPT = """Analyze this video frame for audio description purposes.
You are creating descriptions for blind and visually impaired viewers.

Identify and describe:
1. CHARACTERS: Who is visible? What are they doing? Facial expressions, body language, clothing.
2. ACTIONS: What critical actions are taking place?
3. SETTING: Where does this scene take place? Key environmental details.
4. ON-SCREEN TEXT: Any text, titles, captions, signs visible.
5. EMOTIONAL TONE: What is the emotional atmosphere of this moment?
6. VISUAL STORYTELLING: Any visual metaphors, symbolism, or important visual cues.

Focus on story-critical elements. Use present tense, active voice.
Be concise but thorough - prioritize what a blind viewer NEEDS to know.

Return as JSON:
{
    "characters": [{"name_or_description": "", "action": "", "expression": ""}],
    "setting": "",
    "actions": [""],
    "on_screen_text": [""],
    "emotional_tone": "",
    "visual_elements": [""],
    "narrative_importance": "high|medium|low",
    "suggested_description": ""
}"""


class VideoAnalyzer:
    """Analyzes video frames using LLM vision models"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def analyze_frame(
        self,
        frame_path: str,
        context: Optional[str] = None,
    ) -> dict:
        """
        Analyze a single video frame using LLM vision.

        Args:
            frame_path: Path to the frame image
            context: Optional context from surrounding scenes

        Returns:
            Analysis results as dict
        """
        path = Path(frame_path)
        if not path.exists():
            raise VideoProcessingError(f"Frame not found: {frame_path}")

        # Read and encode frame
        with open(path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        prompt = FRAME_ANALYSIS_PROMPT
        if context:
            prompt += f"\n\nContext from surrounding scenes:\n{context}"

        try:
            result = await self.llm.analyze_image(
                image_data=image_data,
                prompt=prompt,
                mime_type="image/jpeg",
            )
            return result
        except Exception as e:
            logger.error(f"Frame analysis failed for {frame_path}: {e}")
            raise VideoProcessingError(f"Frame analysis failed: {e}")

    async def analyze_scenes(
        self,
        frames: list[dict],
        video_context: Optional[str] = None,
    ) -> list[dict]:
        """
        Analyze multiple frames with scene context.

        Maintains context across frames for consistent character tracking.
        """
        results = []
        running_context = video_context or ""

        for frame in frames:
            analysis = await self.analyze_frame(
                frame_path=frame["path"],
                context=running_context,
            )
            analysis["timestamp"] = frame["timestamp"]
            analysis["frame_number"] = frame["frame_number"]
            results.append(analysis)

            # Build running context from previous analyses
            if analysis.get("suggested_description"):
                running_context += f"\n[{frame['timestamp']:.1f}s] {analysis['suggested_description']}"

        return results
