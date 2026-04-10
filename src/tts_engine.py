import os
import asyncio
import hashlib
from typing import List
from openai import AsyncOpenAI
from dotenv import load_dotenv
from moviepy import AudioFileClip, concatenate_audioclips, AudioClip
from .models import TextSegment

load_dotenv()

class TTSEngine:
    def __init__(self, voice="onyx", model="tts-1-hd"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.voice = voice
        self.model = model
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def _get_cache_path(self, text: str, segment_type: str, voice: str, speed: float) -> str:
        """Generates a unique filename based on content and settings."""
        hash_input = f"{text}_{segment_type}_{voice}_{self.model}_{speed}"
        content_hash = hashlib.md5(hash_input.encode()).hexdigest()
        return os.path.join(self.temp_dir, f"tts_{content_hash}.mp3")

    async def generate_audio(self, segment: TextSegment, voice: str = None, speed: float = 1.0) -> str:
        """
        Generates audio for a segment. 
        Adds 0.5s pauses if type is dialogue.
        """
        voice = voice or self.voice
        output_path = self._get_cache_path(segment.text, segment.type, voice, speed)
        
        if os.path.exists(output_path):
            return output_path

        # 1. Generate Raw TTS
        raw_tts_path = output_path.replace(".mp3", "_raw.mp3")
        response = await self.client.audio.speech.create(
            model=self.model,
            voice=voice,
            input=segment.text,
            speed=speed
        )
        await asyncio.to_thread(response.stream_to_file, raw_tts_path)

        # 2. Add Pauses if Dialogue
        if segment.type == "dialogue":
            final_path = await self._apply_pauses(raw_tts_path, output_path)
            # Clean up raw file
            if os.path.exists(raw_tts_path) and raw_tts_path != output_path:
                os.remove(raw_tts_path)
            return final_path
        else:
            # For narrative, raw is fine (or replace it)
            if os.path.exists(raw_tts_path):
                # Use replace to avoid FileExistsError on Windows
                os.replace(raw_tts_path, output_path)
            return output_path

    async def _apply_pauses(self, input_path: str, output_path: str) -> str:
        """Adds 0.5s silence to the beginning and end of the audio."""
        return await asyncio.to_thread(self.__apply_pauses_sync, input_path, output_path)

    def __apply_pauses_sync(self, input_path: str, output_path: str) -> str:
        audio = AudioFileClip(input_path)
        
        # Create 0.5s silence
        # moviepy doesn't have a direct 'silence' clip but we can make one
        silence = AudioClip(lambda t: 0, duration=0.5, fps=44100)
        
        final_audio = concatenate_audioclips([silence, audio, silence])
        final_audio.write_audiofile(output_path, logger=None)
        
        audio.close()
        silence.close()
        final_audio.close()
        
        return output_path

    async def generate_all(self, segments: List[TextSegment], voice: str = None, speed: float = 1.0) -> List[str]:
        """Processes multiple segments in parallel."""
        tasks = [self.generate_audio(seg, voice=voice, speed=speed) for seg in segments]
        return await asyncio.gather(*tasks)
