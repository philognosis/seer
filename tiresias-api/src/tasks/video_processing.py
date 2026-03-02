"""
Video processing Celery tasks.
Orchestrates the full pipeline from video input to described output.
"""
import logging
from pathlib import Path
from typing import Optional

from src.core.settings import get_settings
from src.services.audio.dialogue_detector import DialogueDetector
from src.services.audio.gap_analyzer import GapAnalyzer
from src.services.audio.mixer import AudioMixer
from src.services.audio.transcription import TranscriptionService
from src.services.description.generator import DescriptionGenerator
from src.services.description.optimizer import DescriptionOptimizer
from src.services.llm.gemini_provider import GeminiProvider
from src.services.tts.voice_manager import VoiceManager
from src.services.video.downloader import VideoDownloader
from src.services.video.frame_extractor import FrameExtractor
from src.services.video.scene_detector import SceneDetectorService
from src.services.video.video_analyzer import VideoAnalyzer
from src.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, name="process_video")
def process_video_task(
    self,
    video_id: str,
    video_path: Optional[str] = None,
    url: Optional[str] = None,
    options: Optional[dict] = None,
) -> dict:
    """
    Main video processing pipeline.

    Steps:
    1. Download video (if URL provided)
    2. Extract audio and detect scenes
    3. Transcribe dialogue and detect gaps
    4. Analyze key frames with LLM
    5. Generate descriptions for gaps
    6. Synthesize descriptions with TTS
    7. Mix audio and produce final output
    """
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(
            _process_video_async(self, video_id, video_path, url, options or {})
        )
        return result
    finally:
        loop.close()


async def _process_video_async(
    task,
    video_id: str,
    video_path: Optional[str],
    url: Optional[str],
    options: dict,
) -> dict:
    """Async implementation of the video processing pipeline"""
    output_dir = Path(settings.OUTPUT_DIR) / video_id
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(settings.TEMP_DIR) / video_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    def update_progress(step: str, progress: int) -> None:
        """Update task progress"""
        task.update_state(
            state="PROGRESS",
            meta={"step": step, "progress": progress, "video_id": video_id},
        )

    try:
        # Step 1: Get video file
        update_progress("Downloading video", 5)

        if url and not video_path:
            downloader = VideoDownloader()
            info = await downloader.download(url, video_id)
            video_path = info["path"]

        if not video_path:
            raise ValueError("No video path or URL provided")

        # Step 2: Extract audio
        update_progress("Extracting audio", 10)
        mixer = AudioMixer(
            ducking_level_db=options.get("ducking_level", -8.0),
        )
        audio_path = str(temp_dir / "audio.wav")
        await mixer.extract_audio(video_path, audio_path)

        # Step 3: Detect scenes
        update_progress("Detecting scenes", 15)
        scene_detector = SceneDetectorService()
        scenes = await scene_detector.detect_scenes(video_path)

        # Step 4: Extract key frames
        update_progress("Extracting key frames", 25)
        frame_extractor = FrameExtractor(output_dir=str(temp_dir))
        frames = await frame_extractor.extract_scene_frames(
            video_path, scenes, video_id
        )

        # Step 5: Transcribe and detect dialogue
        update_progress("Transcribing dialogue", 35)
        dialogue_detector = DialogueDetector()
        dialogue_segments = await dialogue_detector.detect_dialogue(audio_path)

        # Get video metadata for total duration
        metadata = await frame_extractor.get_video_metadata(video_path)
        total_duration = metadata["duration"]

        # Step 6: Find description gaps
        update_progress("Finding description gaps", 45)
        gaps = await dialogue_detector.find_description_gaps(
            dialogue_segments, total_duration
        )

        # Step 7: Analyze frames with LLM
        update_progress("Analyzing visual content", 55)
        llm_provider_name = options.get("llm_provider", "gemini")
        llm = _get_llm_provider(llm_provider_name)
        analyzer = VideoAnalyzer(llm)
        scene_analyses = await analyzer.analyze_scenes(frames)

        # Step 8: Generate descriptions
        update_progress("Generating descriptions", 65)
        gap_analyzer = GapAnalyzer()
        slots = gap_analyzer.analyze_gaps(gaps, scene_analyses)

        generator = DescriptionGenerator(llm)
        descriptions = await generator.generate_descriptions_batch(
            slots,
            scene_analyses,
            density=options.get("description_density", "standard"),
        )

        # Optimize descriptions
        optimizer = DescriptionOptimizer()
        for desc in descriptions:
            desc["text"] = optimizer.optimize(desc["text"], desc.get("max_words"))

        # Step 9: Synthesize TTS
        update_progress("Synthesizing speech", 75)
        voice_manager = VoiceManager()
        voice_id = options.get("voice", "female_us")
        speed = options.get("voice_speed", 1.0)

        description_segments = []
        for i, desc in enumerate(descriptions):
            audio_file = str(temp_dir / f"desc_{i:04d}.mp3")
            await voice_manager.synthesize(
                text=desc["text"],
                voice_id=voice_id,
                output_path=audio_file,
                speed=speed,
            )
            description_segments.append(
                {
                    "audio_path": audio_file,
                    "start_time": desc["timestamp"],
                    "duration": desc["duration"],
                    "text": desc["text"],
                }
            )

        # Step 10: Mix audio
        update_progress("Mixing audio", 85)
        final_video_path = str(output_dir / "final_video.mp4")
        await mixer.mix_descriptions(
            original_video_path=video_path,
            description_segments=description_segments,
            output_path=final_video_path,
        )

        # Step 11: Create standalone description track
        update_progress("Creating description track", 90)
        desc_audio_path = str(output_dir / "descriptions.mp3")
        await mixer.create_description_audio_track(
            description_segments=description_segments,
            total_duration=total_duration,
            output_path=desc_audio_path,
        )

        # Step 12: Save transcript
        update_progress("Saving transcript", 95)
        transcript_path = str(output_dir / "transcript.txt")
        with open(transcript_path, "w") as f:
            f.write("TIRESIAS - Audio Description Transcript\n")
            f.write("=" * 40 + "\n\n")
            for desc in descriptions:
                timestamp = desc["timestamp"]
                minutes = int(timestamp // 60)
                seconds = timestamp % 60
                f.write(f"[{minutes:02d}:{seconds:05.2f}] {desc['text']}\n\n")

        update_progress("Complete", 100)

        return {
            "video_id": video_id,
            "status": "completed",
            "output_path": final_video_path,
            "description_audio_path": desc_audio_path,
            "transcript_path": transcript_path,
            "descriptions_count": len(descriptions),
            "total_duration": total_duration,
        }

    except Exception as e:
        logger.error(f"Video processing failed for {video_id}: {e}", exc_info=True)
        task.update_state(
            state="FAILURE",
            meta={"error": str(e), "video_id": video_id},
        )
        raise


def _get_llm_provider(provider_name: str):
    """Get the appropriate LLM provider"""
    if provider_name == "claude":
        from src.services.llm.claude_provider import ClaudeProvider

        return ClaudeProvider()
    elif provider_name == "openai":
        from src.services.llm.openai_provider import OpenAIProvider

        return OpenAIProvider()
    else:
        return GeminiProvider()
