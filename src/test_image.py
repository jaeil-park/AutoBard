import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessor import TextPreprocessor
from src.image_engine import ImageEngine

async def main():
    print("--- Testing ImageEngine ---")
    
    tp = TextPreprocessor()
    ie = ImageEngine(model="dall-e-3", quality="standard") # Using standard for testing to save cost
    
    # Sample story context
    sample_text = """
    용사는 길게 한숨을 내쉬었다.
    "결국 여기까지 왔군."
    그의 눈앞에는 거대한 마왕성의 문이 서 있었다.
    칠흑같이 어두운 밤, 성문 너머에는 붉은 안개가 피어오르고 있었다.
    """
    
    print("1. Parsing text...")
    segments = tp.process_story(sample_text)
    
    print("\n2. Analyzing scenes and generating images (this will take 15-30 seconds)...")
    image_paths = await ie.process_story_images(segments)
    
    print("\n3. Results:")
    for i, path in enumerate(image_paths):
        if path:
            print(f" - Image {i}: {path}")
        else:
            print(f" - Image {i}: Generation failed.")
            
    print("\n✅ Image Generation Test Completed!")
    print(f"Check the 'temp/' directory for results.")

if __name__ == "__main__":
    asyncio.run(main())
