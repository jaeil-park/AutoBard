import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessor import TextPreprocessor
from src.tts_engine import TTSEngine
from src.subtitle_generator import SubtitleGenerator


async def main():
    print("--- Testing SubtitleGenerator ---")

    tp = TextPreprocessor()
    tts = TTSEngine(voice="onyx")
    sg = SubtitleGenerator()

    sample_text = """
    용사는 길게 한숨을 내쉬었다.
    "결국 여기까지 왔군."
    그의 눈앞에는 거대한 마왕성의 문이 서 있었다.
    """

    print("1. Parsing & generating audio...")
    segments = tp.process_story(sample_text)
    audio_paths = await tts.generate_all(segments)

    print("2. Generating SRT...")
    srt_path = sg.generate_srt(segments, audio_paths)

    print(f"\n3. SRT file created: {srt_path}\n")
    print("--- SRT Content ---")
    with open(srt_path, "r", encoding="utf-8") as f:
        print(f.read())

    total_ms = sg.get_total_duration_ms(audio_paths)
    print(f"Total video duration: {total_ms / 1000:.2f}s")
    print("\n✅ Subtitle generation test passed!")


if __name__ == "__main__":
    asyncio.run(main())
