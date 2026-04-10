import os
import asyncio
import json
from typing import List
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .models import TextSegment

load_dotenv()

class ImageEngine:
    def __init__(self, model="dall-e-3", size="1024x1024", quality="hd"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.size = size
        self.quality = quality
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    async def analyze_scenes(self, segments: List[TextSegment]) -> List[str]:
        """
        Analyzes segments to extract 1-2 visually representative prompts.
        """
        full_text = "\n".join([f"[{seg.type}] {seg.text}" for seg in segments])
        
        system_prompt = """
        You are a visual scene analyzer for a fantasy web novel. 
        Your task is to summarize the given text into 1 or 2 visual descriptions for AI image generation. 
        Focus on:
        1. The main subject (character, creature).
        2. The setting (background, environment).
        3. The mood (lighting, atmosphere).
        
        Output only a JSON array of strings, where each string is a concise visual description in English.
        Example: ["An elven knight standing in a rainy forest, cinematic lighting", "A dark castle gate under a blood moon"]
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this story and extract 1-2 key visual scenes:\n\n{full_text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            # Find the array in the object (e.g., {"scenes": [...]})
            if "scenes" in result:
                return result["scenes"]
            return list(result.values())[0] if result.values() else []
            
        except Exception as e:
            print(f"Error analyzing scenes: {e}")
            return ["A mystical fantasy landscape, high resolution"]

    async def generate_image(self, visual_description: str) -> str:
        """
        Generates an image via DALL-E 3 and returns the local file path.
        """
        style_prompt = (
            f"Detailed digital painting of {visual_description}, "
            "in a high-fantasy web novel illustration style, "
            "intricate details, cinematic composition, soft ambient lighting, "
            "vibrant fantasy atmosphere, high resolution, sharp focus."
        )
        
        try:
            response = await self.client.images.generate(
                model=self.model,
                prompt=style_prompt,
                size=self.size,
                quality=self.quality,
                n=1,
            )
            
            image_url = response.data[0].url
            # Download the image
            import aiohttp
            import hashlib
            
            prompt_hash = hashlib.md5(visual_description.encode()).hexdigest()
            output_path = os.path.join(self.temp_dir, f"img_{prompt_hash}.png")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(output_path, "wb") as f:
                            f.write(content)
                        return output_path
            
            return ""
        except Exception as e:
            print(f"Error generating image: {e}")
            return ""

    async def process_story_images(self, segments: List[TextSegment]) -> List[str]:
        """Executes full analysis and generation pipeline."""
        scene_prompts = await self.analyze_scenes(segments)
        image_tasks = [self.generate_image(p) for p in scene_prompts[:2]]  # Limit 2
        return await asyncio.gather(*image_tasks)
