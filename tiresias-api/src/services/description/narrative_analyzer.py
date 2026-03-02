"""
Narrative analysis service.
Provides story intelligence for better description prioritization.
"""
import logging
from typing import Optional

from src.services.llm.provider_base import LLMProvider

logger = logging.getLogger(__name__)

NARRATIVE_ANALYSIS_PROMPT = """Analyze the narrative structure of these scene descriptions
to help prioritize which visual elements are most story-critical.

Scene descriptions (chronological):
{scenes}

For each scene, rate the narrative importance (1-10) of:
1. Character actions and expressions
2. Setting/environment changes
3. On-screen text or symbols
4. Emotional atmosphere
5. Visual metaphors or foreshadowing

Return as JSON array:
[
    {{
        "timestamp": <float>,
        "narrative_importance": "high|medium|low",
        "key_elements": ["element1", "element2"],
        "character_development": true|false,
        "plot_point": true|false,
        "setting_change": true|false,
        "priority_score": <1-10>
    }}
]"""


class NarrativeAnalyzer:
    """Analyzes narrative structure for description prioritization"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def analyze_narrative(
        self,
        scene_analyses: list[dict],
    ) -> list[dict]:
        """
        Analyze the narrative arc of a video's scenes.

        Uses the LLM to understand story structure and prioritize
        which visual elements are most important to describe.
        """
        if not scene_analyses:
            return []

        # Format scenes for analysis
        scenes_text = ""
        for scene in scene_analyses:
            ts = scene.get("timestamp", 0)
            desc = scene.get("suggested_description", str(scene))
            scenes_text += f"\n[{ts:.1f}s] {desc}"

        prompt = NARRATIVE_ANALYSIS_PROMPT.format(scenes=scenes_text)

        try:
            response = await self.llm.generate_text(
                prompt=prompt,
                max_tokens=2048,
                temperature=0.3,
            )

            # Parse response
            import json

            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]

            return json.loads(text.strip())

        except Exception as e:
            logger.warning(f"Narrative analysis failed: {e}")
            # Return basic priority assignments
            return [
                {
                    "timestamp": scene.get("timestamp", 0),
                    "narrative_importance": "medium",
                    "priority_score": 5,
                }
                for scene in scene_analyses
            ]
