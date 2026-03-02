"""
Audio description text generation service.
Creates concise, story-critical descriptions using LLM intelligence.
"""
import logging
from typing import Optional

from src.services.audio.gap_analyzer import DescriptionSlot
from src.services.llm.provider_base import LLMProvider

logger = logging.getLogger(__name__)

DESCRIPTION_SYSTEM_PROMPT = """You are an expert audio describer for blind and visually impaired viewers.

Your descriptions must:
1. Use PRESENT TENSE, ACTIVE VOICE
2. Be CONCISE - every word must earn its place
3. Focus on STORY-CRITICAL visual information
4. NEVER describe what can be heard (dialogue, music, sound effects)
5. Maintain CHARACTER CONSISTENCY (use established names)
6. Convey EMOTIONAL TONE through word choice
7. Prioritize: Actions > Characters > Setting > Details

Rules:
- Start with the most important information
- Avoid subjective interpretations unless clearly implied
- Use specific, vivid verbs (not "is" or "goes")
- Name characters once identified, use descriptions before that
- Include critical on-screen text
- Fit EXACTLY within the word limit specified"""


class DescriptionGenerator:
    """Generates audio descriptions using LLM"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def generate_description(
        self,
        slot: DescriptionSlot,
        scene_analysis: dict,
        context: str = "",
        density: str = "standard",
    ) -> str:
        """
        Generate a description for a specific slot.

        Args:
            slot: The DescriptionSlot to fill
            scene_analysis: Analysis of the scene to describe
            context: Running context of previous descriptions
            density: Description density (minimal, standard, detailed)

        Returns:
            Generated description text
        """
        max_words = slot.max_words
        if density == "minimal":
            max_words = min(max_words, int(max_words * 0.6))
        elif density == "detailed":
            max_words = max_words  # Use full allocation

        prompt = self._build_prompt(scene_analysis, max_words, context, density)

        text = await self.llm.generate_text(
            prompt=prompt,
            system_prompt=DESCRIPTION_SYSTEM_PROMPT,
            max_tokens=max_words * 3,  # Tokens ~= 0.75 words
            temperature=0.5,
        )

        # Ensure description fits within word limit
        words = text.strip().split()
        if len(words) > max_words:
            text = " ".join(words[:max_words])
            # Try to end at a sentence boundary
            for punct in [".", "!", ";"]:
                idx = text.rfind(punct)
                if idx > len(text) * 0.6:
                    text = text[: idx + 1]
                    break

        return text.strip()

    async def generate_descriptions_batch(
        self,
        slots: list[DescriptionSlot],
        scene_analyses: list[dict],
        density: str = "standard",
    ) -> list[dict]:
        """
        Generate descriptions for multiple slots with running context.

        Maintains character and narrative consistency across descriptions.
        """
        descriptions = []
        running_context = ""

        for slot in sorted(slots, key=lambda s: s.scene_timestamp):
            # Find matching scene analysis
            analysis = self._find_matching_analysis(slot, scene_analyses)
            if not analysis:
                continue

            text = await self.generate_description(
                slot=slot,
                scene_analysis=analysis,
                context=running_context,
                density=density,
            )

            descriptions.append(
                {
                    "timestamp": slot.gap_start,
                    "duration": slot.available_duration,
                    "text": text,
                    "scene_timestamp": slot.scene_timestamp,
                    "priority": slot.priority,
                    "max_words": slot.max_words,
                }
            )

            running_context += f"\n[{slot.scene_timestamp:.1f}s] {text}"

        logger.info(f"Generated {len(descriptions)} descriptions")
        return descriptions

    def _build_prompt(
        self,
        analysis: dict,
        max_words: int,
        context: str,
        density: str,
    ) -> str:
        """Build the description generation prompt"""
        prompt = f"""Generate an audio description in EXACTLY {max_words} words or fewer.

Scene Analysis:
{self._format_analysis(analysis)}

Previous descriptions for context:
{context if context else "(This is the first description)"}

Density level: {density}
Maximum words: {max_words}

Generate ONLY the description text. No metadata, no quotes, no explanations."""
        return prompt

    def _format_analysis(self, analysis: dict) -> str:
        """Format scene analysis for the prompt"""
        parts = []
        if analysis.get("characters"):
            chars = analysis["characters"]
            if isinstance(chars, list):
                for c in chars:
                    if isinstance(c, dict):
                        parts.append(
                            f"- Character: {c.get('name_or_description', 'Unknown')} - "
                            f"{c.get('action', '')} ({c.get('expression', '')})"
                        )
        if analysis.get("setting"):
            parts.append(f"- Setting: {analysis['setting']}")
        if analysis.get("actions"):
            for action in analysis["actions"]:
                parts.append(f"- Action: {action}")
        if analysis.get("emotional_tone"):
            parts.append(f"- Tone: {analysis['emotional_tone']}")
        if analysis.get("on_screen_text"):
            for text in analysis["on_screen_text"]:
                parts.append(f"- On-screen text: {text}")

        return "\n".join(parts) if parts else str(analysis)

    def _find_matching_analysis(
        self, slot: DescriptionSlot, analyses: list[dict]
    ) -> Optional[dict]:
        """Find the scene analysis closest to a slot's timestamp"""
        if not analyses:
            return None

        best = None
        best_distance = float("inf")
        for analysis in analyses:
            ts = analysis.get("timestamp", 0)
            distance = abs(ts - slot.scene_timestamp)
            if distance < best_distance:
                best = analysis
                best_distance = distance

        return best
