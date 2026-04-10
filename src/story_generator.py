import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class StoryGenerator:
    """
    Generates modernized Korean folktales and legends using GPT-4o-mini.
    Optimized for the 'Uncle Reader' persona.
    """

    def __init__(self, model="gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    async def generate_story(self, topic: str, next_topic: str = None) -> dict:
        """
        Generates a story WITH METADATA (genre, voice, teaser).
        Returns a dict: {script, title, genre, voice, speed, teaser_text}
        """
        system_prompt = """
        You are a master storyteller and content director.
        Create a STORY SCRIPT and METADATA serialized as JSON.
        
        JSON STRUCTURE:
        - 'title': Catchy title
        - 'script': The storytelling text with [📝 NARRATIVE] and [🗨️ DIALOGUE] tags.
        - 'genre': 'horror', 'legend', or 'folktale'
        - 'voice': 'fable' for horror, 'onyx' for legend/folktale, 'echo' for tense thriller.
        - 'speed': 0.85 (horror) to 1.0 (folktale)
        - 'teaser_text': A 1-sentence hook for the NEXT episode.
        
        RULES:
        1. Script must be dramatic (500-800 characters).
        2. Keep the 'Uncle Reader' persona but adjust tone for genre.
        3. Teaser should be mysterious: "Next time: [Hook about next_topic]"
        """

        user_input = f"Topic: {topic}. Next Topic: {next_topic or 'Unknown mysterious legend'}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            print(f"📖 Story Metadata: Genre={data.get('genre')}, Voice={data.get('voice')}, Teaser={'Yes' if data.get('teaser_text') else 'No'}")
            return data
            
        except Exception as e:
            print(f"Error generating story: {e}")
            return {
                "title": "신비한 이야기",
                "script": "[📝 NARRATIVE] 이야기를 불러오는 중에 신비한 안개가 끼었구먼. 잠시 후에 다시 시도해 보게나.",
                "genre": "legend",
                "voice": "onyx",
                "speed": 1.0,
                "teaser_text": "내일 밤, 더 놀라운 이야기가 찾아옵니다."
            }

    async def generate_title(self, story_content: str) -> str:
        """Deprecated: generate_story now returns title directly in dict."""
        return "제목 없음"
