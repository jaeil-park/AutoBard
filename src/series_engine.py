import os
import json
import asyncio
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class SeriesEngine:
    """
    Handles multi-episode story planning and script generation.
    Ensures continuity and dramatic cliffhangers across a series.
    """

    def __init__(self, model="gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    async def plan_series(self, topic: str, count: int = 5) -> Dict:
        """
        Creates a high-level roadmap for the entire series.
        """
        print(f"Planning a {count}-episode series for: {topic}...")
        
        system_prompt = f"""
        You are a showrunner for a web novel series. 
        Plan a {count}-episode series based on the user's topic.
        
        Output must be a valid JSON object with:
        - 'series_title': Catchy title for the season
        - 'episodes': A list of {count} objects, each with:
            - 'ep_num': episode number
            - 'title': episode title
            - 'summary': what happens in this episode (2-3 sentences)
            - 'cliffhanger': the specific hook at the end
        
        Themes: Korean Folktales, Legends, or Fantasy.
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Topic: {topic}"}
            ],
            response_format={"type": "json_object"}
        )
        
        plan = json.loads(response.choices[0].message.content)
        
        # Save plan for future reference
        plan_path = os.path.join(self.temp_dir, f"series_{topic.replace(' ', '_')}_plan.json")
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=4, ensure_ascii=False)
            
        return plan

    async def generate_episode_script(self, plan: Dict, ep_num: int) -> str:
        """
        Generates the actual script for a specific episode based on the series plan.
        """
        ep_info = next((e for e in plan['episodes'] if e['ep_num'] == ep_num), None)
        if not ep_info:
            return ""

        system_prompt = """
        You are a storyteller specializing in Korean legends.
        Write a dramatic storytelling script (500-800 chars) for an episode in a SERIES.
        
        FORMAT RULES:
        1. Use [📝 NARRATIVE] and [🗨️ DIALOGUE] tags.
        2. Ensure the episode ends with the CLIFFHANGER provided in the plan.
        3. Do NOT provide a conclusion or a 'happily ever after' yet.
        """

        user_content = f"""
        Series: {plan['series_title']}
        Current Episode: {ep_num} - {ep_info['title']}
        Summary: {ep_info['summary']}
        Mandatory Cliffhanger: {ep_info['cliffhanger']}
        
        Write the full script in Korean.
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
