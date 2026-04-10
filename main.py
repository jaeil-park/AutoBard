"""
AutoBard - AI Fantasy Web Novel to Video Pipeline
Main orchestrator: text → TTS + image + subtitle → video → upload
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.preprocessor import TextPreprocessor
from src.tts_engine import TTSEngine
from src.image_engine import ImageEngine
from src.subtitle_generator import SubtitleGenerator
from src.video_renderer import VideoRenderer
from src.youtube_uploader import YouTubeUploader
from src.story_generator import StoryGenerator
from src.series_engine import SeriesEngine
from src.auto_scheduler import AutoScheduler

load_dotenv()


class AutoBardPipeline:
    """End-to-end pipeline for a single story episode."""

    def __init__(
        self,
        voice: str = "onyx",
        image_quality: str = "standard",
        output_dir: str = "output",
    ):
        self.preprocessor = TextPreprocessor()
        self.tts = TTSEngine(voice=voice)
        self.image_engine = ImageEngine(quality=image_quality)
        self.subtitle_gen = SubtitleGenerator()
        self.renderer = VideoRenderer(output_dir=output_dir)
        self.uploader = YouTubeUploader()
        self.story_engine = StoryGenerator()
        self.series_engine = SeriesEngine()
        self.scheduler = AutoScheduler()

    async def run(
        self,
        story_text: str,
        episode_title: str,
        output_filename: str = "episode.mp4",
        skip_images: bool = False,
        existing_image_paths: list = None,
        upload: bool = False,
        auto_topic: str = None,
        voice: str = None,
        speed: float = 1.0,
        teaser_text: str = None
    ) -> str:
        """
        Runs the full pipeline.
        Returns the path to the final MP4.
        """
        # 1. Generate Story if topic provided
        story_data = None
        if auto_topic:
            print(f"[0/6] ✨ Generating original folktale for: {auto_topic}...")
            story_data = await self.story_engine.generate_story(auto_topic)
            story_text = story_data['script']
            episode_title = f"{story_data['title']} ({story_data['genre'].capitalize()})"
            voice = story_data.get('voice', self.voice)
            speed = story_data.get('speed', 1.0)
            teaser_text = story_data.get('teaser_text')

        # 2. Preprocess Text
        print(f"[1/6] 📝 Preprocessing story: {episode_title}")
        segments = self.preprocessor.process_story(story_text)

        # 3. Generate Audio
        voice = voice or self.voice
        print(f"[2/6] 🎙️  Generating TTS audio ({voice.capitalize()}, {speed}x)...")
        audio_paths = await self.tts.generate_all(segments, voice=voice, speed=speed)
        
        total_s = sum(
            __import__("moviepy").AudioFileClip(p).duration for p in audio_paths
        )
        print(f"      → Total audio duration: {total_s:.1f}s")

        # ── Step 3: Images ───────────────────────────────────────────
        if existing_image_paths:
            image_paths = existing_image_paths
            print(f"\n[3/5] 🎨 Using {len(image_paths)} pre-generated image(s).")
        elif skip_images:
            image_paths = [
                p for p in Path("temp").glob("*.png") if p.stat().st_size > 0
            ]
            image_paths = [str(p) for p in image_paths[:2]]
            print(f"\n[3/5] 🎨 Using {len(image_paths)} cached image(s) from temp/.")
        else:
            print("\n[3/5] 🎨 Generating story images via DALL-E 3...")
            image_paths = await self.image_engine.process_story_images(segments)
            print(f"      → {len(image_paths)} image(s) generated.")

        if not image_paths:
            raise ValueError("No images available for rendering.")

        # ── Step 4: Subtitles ────────────────────────────────────────
        print("\n[4/5] 📄 Generating SRT subtitles...")
        srt_path = self.subtitle_gen.generate_srt(
            segments, audio_paths, output_filename=f"{Path(output_filename).stem}.srt"
        )
        print(f"      → SRT saved: {srt_path}")

        # 6. Render Video
        teaser_text = teaser_text or (story_data.get('teaser_text') if story_data else None)
        print(f"[5/6] 🎬 Rendering final video (Teaser: {'Yes' if teaser_text else 'No'})...")
        output_path = self.renderer.render(
            image_paths=image_paths,
            segments=segments,
            audio_paths=audio_paths,
            output_filename=output_filename,
            teaser_text=teaser_text
        )

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n{'=' * 60}")
        print(f"✅ Video rendering complete!")
        print(f"   Output : {output_path} ({size_mb:.1f} MB)")
        print(f"   SRT    : {srt_path}")
        print(f"{'=' * 60}")

        # ── Step 6: Upload (Optional) ───────────────────────────────
        if upload:
            print("\n[6/6] 🚀 Uploading to YouTube (Private)...")
            video_id = self.uploader.upload(
                video_path=output_path,
                title=episode_title,
                description=f"AutoBard가 읽어주는 판타지 웹소설: {episode_title}\n\n#판타지 #웹소설 #AI",
            )
            print(f"      → Uploaded! Video ID: {video_id}")

        return output_path


# ── CLI entry point ───────────────────────────────────────────────────
import argparse

async def main():
    parser = argparse.ArgumentParser(description="AutoBard - AI Video Generator")
    parser.add_argument("--topic", type=str, help="Topic for AI story generation (e.g., '구미호', '도깨비')")
    parser.add_argument("--text", type=str, help="Manually provide story text")
    parser.add_argument("--title", type=str, default="오늘의 이야기", help="Episode title")
    parser.add_argument("--upload", action="store_true", help="Upload result to YouTube (Private)")
    parser.add_argument("--skip_images", action="store_true", help="Use cached images from temp/")
    parser.add_argument("--voice", type=str, default="onyx", help="TTS voice (onyx, alloy, echo, etc.)")
    
    parser.add_argument("--series", type=str, help="Launch a series for this topic")
    parser.add_argument("--count", type=int, default=1, help="Number of episodes in series")
    parser.add_argument("--auto", action="store_true", help="Autonomous mode (picks topic automatically)")
    
    args = parser.parse_args()

    pipeline = AutoBardPipeline(voice=args.voice, image_quality="standard")
    
    # ── Option 0: Auto Mode (Daily Scheduler) ────────────────────────
    if args.auto:
        print("🤖 Auto Mode Enabled: Planning today's scary/cool story...")
        today, tomorrow = await pipeline.scheduler.get_daily_topic()
        
        story_data = await pipeline.story_engine.generate_story(today, next_topic=tomorrow)
        
        await pipeline.run(
            story_text=story_data['script'],
            episode_title=f"{story_data['title']} ({story_data['genre'].capitalize()})",
            output_filename=f"daily_{today.replace(' ', '_')}.mp4",
            skip_images=args.skip_images,
            upload=args.upload,
            voice=story_data.get('voice'),
            speed=story_data.get('speed', 1.0),
            teaser_text=story_data.get('teaser_text')
        )
        print(f"✅ Daily automation complete for topic: {today}")
        return

    # ── Option 1: Series Mode ────────────────────────────────────────
    if args.series:
        plan = await pipeline.series_engine.plan_series(args.series, args.count)
        print(f"\n📺 Series Plan Confirmed: {plan['series_title']}")
        
        for ep in plan['episodes']:
            ep_num = ep['ep_num']
            print(f"\n🚀 Rendering Episode {ep_num}: {ep['title']}")
            
            script = await pipeline.series_engine.generate_episode_script(plan, ep_num)
            
            await pipeline.run(
                story_text=script,
                episode_title=f"{plan['series_title']} - {ep['title']}",
                output_filename=f"{args.series.replace(' ', '_')}_ep{ep_num:02d}.mp4",
                skip_images=args.skip_images,
                upload=args.upload
            )
        print(f"\n✅ All {args.count} episodes of '{plan['series_title']}' are ready!")
        return

    # ── Option 2: Single Mode ────────────────────────────────────────
    output = await pipeline.run(
        story_text=args.text or "",
        episode_title=args.title,
        output_filename="auto_episode.mp4",
        skip_images=args.skip_images,
        upload=args.upload,
        auto_topic=args.topic
    )
    
    print(f"\n👉 Process Complete: {os.path.abspath(output)}")

if __name__ == "__main__":
    asyncio.run(main())
