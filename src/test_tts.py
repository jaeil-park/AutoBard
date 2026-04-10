import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessor import TextPreprocessor
from src.tts_engine import TTSEngine

async def main():
    print("--- Testing TTSEngine ---")
    
    tp = TextPreprocessor()
    tts = TTSEngine(voice="onyx")
    
    # Sample text from a fantasy webnovel style
    sample_text = """
    용사는 길게 한숨을 내쉬었다.
    "결국 여기까지 왔군."
    그의 눈앞에는 거대한 마왕성의 문이 서 있었다.
    """
    
    print("1. Parsing text...")
    segments = tp.process_story(sample_text)
    for i, seg in enumerate(segments):
        print(f" Segment {i}: {seg}")
        
    print("\n2. Generating audio (this might take a few seconds)...")
    audio_paths = await tts.generate_all(segments)
    
    print("\n3. Results:")
    for i, path in enumerate(audio_paths):
        size = os.path.getsize(path) / 1024
        print(f" - Segment {i} audio: {path} ({size:.2f} KB)")
        
    print("\n✅ TTS Generation Test Completed!")
    print(f"Generated files are in the 'temp/' directory.")

if __name__ == "__main__":
    asyncio.run(main())
