import os
from typing import List, Tuple
from moviepy import AudioFileClip
from .models import TextSegment


class SubtitleGenerator:
    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def _ms_to_srt_time(self, ms: float) -> str:
        """Converts milliseconds to SRT timestamp format: HH:MM:SS,mmm"""
        total_seconds = int(ms // 1000)
        milliseconds = int(ms % 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def _get_audio_duration_ms(self, audio_path: str) -> float:
        """Returns audio duration in milliseconds using MoviePy."""
        clip = AudioFileClip(audio_path)
        duration = clip.duration * 1000
        clip.close()
        return duration

    def _clean_text_for_subtitle(self, text: str) -> str:
        """Removes surrounding quotes from dialogue for cleaner subtitles."""
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        return text

    def generate_srt(
        self,
        segments: List[TextSegment],
        audio_paths: List[str],
        output_filename: str = "subtitles.srt",
    ) -> str:
        """
        Generates a synchronized SRT file from segments and their audio files.
        Returns the path to the created SRT file.
        """
        if len(segments) != len(audio_paths):
            raise ValueError(
                f"Segments ({len(segments)}) and audio_paths ({len(audio_paths)}) must have the same count."
            )

        srt_blocks = []
        cursor_ms = 0.0

        for i, (seg, audio_path) in enumerate(zip(segments, audio_paths), start=1):
            duration_ms = self._get_audio_duration_ms(audio_path)
            start_ms = cursor_ms
            end_ms = cursor_ms + duration_ms

            start_ts = self._ms_to_srt_time(start_ms)
            end_ts = self._ms_to_srt_time(end_ms)

            clean_text = self._clean_text_for_subtitle(seg.text)

            srt_block = f"{i}\n{start_ts} --> {end_ts}\n{clean_text}\n"
            srt_blocks.append(srt_block)

            cursor_ms = end_ms

        srt_content = "\n".join(srt_blocks)
        output_path = os.path.join(self.temp_dir, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        return output_path

    def get_total_duration_ms(self, audio_paths: List[str]) -> float:
        """Returns the total duration of all audio files combined."""
        return sum(self._get_audio_duration_ms(p) for p in audio_paths)
