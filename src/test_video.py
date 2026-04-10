import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessor import TextPreprocessor
from src.tts_engine import TTSEngine
from src.image_engine import ImageEngine
from src.video_renderer import VideoRenderer


async def main():
    print("--- Testing VideoRenderer (Full Pipeline) ---")

    tp = TextPreprocessor()
    tts = TTSEngine(voice="onyx")
    ie = ImageEngine(model="dall-e-3", quality="standard")
    vr = VideoRenderer(output_dir="output")

    sample_text = """
    용사는 길게 한숨을 내쉬었다.
    "결국 여기까지 왔군."
    그의 눈앞에는 거대한 마왕성의 문이 서 있었다.
    """

    print("1. Parsing text...")
    segments = tp.process_story(sample_text)

    print("2. Generating TTS audio (cached if exists)...")
    audio_paths = await tts.generate_all(segments)

    print("3. Using cached images from temp/ ...")
    image_paths = [f for f in os.listdir("temp") if f.endswith(".png")]
    image_paths = [os.path.join("temp", p) for p in image_paths[:2]]

    if not image_paths:
        print("   No cached images found — generating new ones...")
        image_paths = await ie.process_story_images(segments)

    print(f"   Using images: {image_paths}")

    print("4. Rendering video (this may take 30-60s)...")
    output_path = vr.render(
        image_paths=image_paths,
        segments=segments,
        audio_paths=audio_paths,
        output_filename="test_episode.mp4",
    )

    print(f"\n✅ Video rendered: {output_path}")
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   File size: {size_mb:.2f} MB")


if __name__ == "__main__":
    asyncio.run(main())
