import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.story_generator import StoryGenerator

async def test_story():
    gen = StoryGenerator()
    topic = "도깨비와 혹부리 영감"
    print(f"--- Generating Story for: {topic} ---")
    
    story = await gen.generate_story(topic)
    print("\n[Generated Story]")
    print(story)
    
    title = await gen.generate_title(story)
    print(f"\n[Generated Title]\n{title}")

if __name__ == "__main__":
    asyncio.run(test_story())
