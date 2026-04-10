import os
import json
import random
import asyncio
from typing import Optional
from src.story_generator import StoryGenerator

class AutoScheduler:
    """
    Manages daily topic selection and state (today's topic vs next topic for teaser).
    """
    
    def __init__(self, state_file="temp/scheduler_state.json"):
        self.state_file = state_file
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self.story_engine = StoryGenerator()
        
    def load_state(self) -> dict:
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"next_topic": None, "history": []}

    def save_state(self, state: dict):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)

    async def get_daily_topic(self) -> tuple:
        """Determines today's topic and tomorrow's topic."""
        state = self.load_state()
        
        # 1. Today's topic is what was 'next' yesterday, or a fresh one
        today_topic = state.get("next_topic")
        if not today_topic:
            today_topic = await self._generate_fresh_topic()
            
        # 2. Pick tomorrow's topic now (for teaser)
        tomorrow_topic = await self._generate_fresh_topic(exclude=[today_topic] + state.get("history", []))
        
        # 3. Update state
        state["next_topic"] = tomorrow_topic
        state["history"].append(today_topic)
        if len(state["history"]) > 50: # Keep history manageable
            state["history"].pop(0)
        self.save_state(state)
        
        return today_topic, tomorrow_topic

    async def _generate_fresh_topic(self, exclude=None) -> str:
        """Uses AI to invent a unique, never-before-seen Korean urban legend or horror topic."""
        exclude = exclude or []
        
        # Randomly pick a genre focus for variety
        genres = ["Modern Korean Urban Legend", "Joseon Dynasty Horror", "Traditional Folk Mystery", "High-rise Apartment Ghost Story"]
        focus = random.choice(genres)
        
        prompt = f"""
        Invent a unique, catchy Korean storytelling topic focus on {focus}.
        It should be one sentence (e.g., 'The Ghost of the High-Rise Lift' or 'The Haunted Rice Chest').
        Avoid topics in this list: {exclude}
        Return ONLY the topic text.
        """
        
        try:
            response = await self.story_engine.client.chat.completions.create(
                model=self.story_engine.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            return response.choices[0].message.content.strip().replace('"', '')
        except:
            return "신비로운 숲의 기담"

async def main():
    scheduler = AutoScheduler()
    today, tomorrow = await scheduler.get_daily_topic()
    print(f"📅 Today's Topic: {today}")
    print(f"🔮 Tomorrow's Teaser: {tomorrow}")

if __name__ == "__main__":
    asyncio.run(main())
