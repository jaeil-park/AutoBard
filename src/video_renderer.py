import os
import asyncio
from typing import List
from moviepy import (
    AudioFileClip,
    ImageClip,
    concatenate_audioclips,
    CompositeVideoClip,
    TextClip,
    concatenate_videoclips,
    ColorClip
)
from .models import TextSegment
from .subtitle_generator import SubtitleGenerator
import emoji
import re


class VideoRenderer:
    """
    Assembles image(s), audio segments, and subtitle overlays into a final MP4.

    Layout:
    - 16:9 widescreen (1920x1080) for YouTube / TikTok long-form
    - Subtitles: Pretendard (or fallback), 32pt, centered, bottom 15%,
      white text on a semi-transparent dark bar (30% opacity).
    """

    OUTPUT_WIDTH = 1920
    OUTPUT_HEIGHT = 1080
    FPS = 30
    SUBTITLE_FONT_SIZE = 50
    SUBTITLE_Y_RATIO = 0.85  # bottom 15% — top of bar at 85% of height

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.sg = SubtitleGenerator()

    # ------------------------------------------------------------------
    # Ken Burns zoom effect using moviepy resize transform
    # ------------------------------------------------------------------
    def _make_ken_burns_clip(self, image_path: str, duration: float) -> ImageClip:
        """
        Creates an ImageClip with a subtle Ken Burns zoom-in effect.
        Start scale: 1.0 → End scale: 1.08 over the clip duration.
        """
        clip = ImageClip(image_path, duration=duration)
        # Resize to fill the frame first
        clip = clip.resized(height=self.OUTPUT_HEIGHT)
        if clip.w < self.OUTPUT_WIDTH:
            clip = clip.resized(width=self.OUTPUT_WIDTH)

        def zoom(t):
            scale = 1.0 + 0.08 * (t / duration)
            return scale

        clip = clip.resized(zoom).with_position("center")
        return clip

    # ------------------------------------------------------------------
    # Subtitle overlay
    # ------------------------------------------------------------------
    @staticmethod
    def _resolve_font() -> str:
        """Resolves the best available Korean-compatible font path for Win/Linux."""
        # Linux (GitHub Actions / Ubuntu)
        if os.name != 'nt':
            linux_candidates = [
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
                "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
            ]
            for path in linux_candidates:
                if os.path.exists(path):
                    return path
            return "DejaVu Sans" # Ubuntu default fallback

        # Windows
        candidates = [
            r"C:\Windows\Fonts\NotoSansKR-VF.ttf",   # Noto Sans KR
            r"C:\Windows\Fonts\malgun.ttf",           # Malgun Gothic
            r"C:\Windows\Fonts\arialuni.ttf",         # Arial Unicode MS
            r"C:\Windows\Fonts\seguiemj.ttf",         # Segoe UI Emoji
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return "Arial"  # Basic fallback

    def _sanitize_text(self, text: str) -> str:
        """
        Cleans text for subtitles to avoid 'boxes' in video rendering.
        - Removes emojis via 'emoji' package.
        - Keeps Korean, English, numbers, and basic punctuation.
        """
        # 1. Remove emojis
        text = emoji.replace_emoji(text, replace='')
        
        # 2. Keep only supported characters (Korean, Alphanumeric, Basic Symbols)
        # re.sub logic to keep: \uac00-\ud7a3 (KR), a-zA-Z, 0-9, common punct
        pattern = re.compile(r'[^ \uac00-\ud7a3\u1100-\u11ff\u3130-\u318f가-힣a-zA-Z0-9\s.,!?\"\']+')
        cleaned = pattern.sub('', text)
        
        return cleaned.strip()

    def _make_subtitle_overlay(self, text: str, duration: float) -> TextClip:
        """Creates a subtitle text clip with a drop-shadow effect."""
        font_path = self._resolve_font()
        txt = TextClip(
            text=text,
            font=font_path,
            font_size=self.SUBTITLE_FONT_SIZE,
            color="white",
            stroke_color="black",
            stroke_width=3,
            method="caption",
            size=(self.OUTPUT_WIDTH - 160, None),
        ).with_duration(duration)

        txt_y = int(self.OUTPUT_HEIGHT * self.SUBTITLE_Y_RATIO)
        txt = txt.with_position(("center", txt_y))
        return txt

    def _make_teaser_clip(self, teaser_text: str) -> CompositeVideoClip:
        """Creates a 'Next Episode' teaser clip with a black background."""
        duration = 5.0
        # 1. Background (Black)
        bg = ColorClip(size=(self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT), color=(0, 0, 0), duration=duration)
        
        # 2. "Next Episode" Label
        label = TextClip(
            text="─ 다음 이야기 ─",
            font=self._resolve_font(),
            font_size=40,
            color="lightgrey",
            method="caption",
            size=(self.OUTPUT_WIDTH, 100)
        ).with_duration(duration).with_position(("center", 400))
        
        # 3. Teaser Content
        content = TextClip(
            text=teaser_text,
            font=self._resolve_font(),
            font_size=45,
            color="white",
            method="caption",
            size=(self.OUTPUT_WIDTH - 200, None)
        ).with_duration(duration).with_position(("center", 550))
        
        return CompositeVideoClip([bg, label, content], size=(self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT))

    # ------------------------------------------------------------------
    # Main assembly pipeline
    # ------------------------------------------------------------------
    def render(
        self,
        image_paths: List[str],
        segments: List[TextSegment],
        audio_paths: List[str],
        output_filename: str = "episode.mp4",
        teaser_text: str = None
    ) -> str:
        """
        Renders the final video.
        - image_paths: 1 or 2 images; repeated/looped to cover full duration.
        - segments + audio_paths: matched pairs for timing.
        - Returns path to output MP4.
        """
        # 1. Build combined audio & measure timings
        audio_clips = [AudioFileClip(p) for p in audio_paths]
        durations = [c.duration for c in audio_clips]
        total_duration = sum(durations)
        combined_audio = concatenate_audioclips(audio_clips)

        # 2. Build background video from images (Ken Burns)
        # Distribute images evenly across total duration
        if len(image_paths) == 1:
            image_durations = [total_duration]
        else:
            half = total_duration / len(image_paths)
            image_durations = [half] * len(image_paths)

        bg_clips = [
            self._make_ken_burns_clip(img, dur)
            for img, dur in zip(image_paths, image_durations)
        ]
        bg_video = concatenate_videoclips(bg_clips)

        # 3. Build subtitle layers — one TextClip per segment, positioned in time
        subtitle_clips = []
        cursor = 0.0
        for seg, dur in zip(segments, durations):
            original_text = seg.text.strip('"')
            clean_text = self._sanitize_text(original_text)
            
            txt_clip = self._make_subtitle_overlay(clean_text, dur)
            txt_clip = txt_clip.with_start(cursor)
            subtitle_clips.append(txt_clip)
            cursor += dur

        # 4. Composite main video
        all_layers = [bg_video] + subtitle_clips
        main_video = CompositeVideoClip(all_layers, size=(self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT))
        main_video = main_video.with_audio(combined_audio)
        main_video = main_video.with_duration(total_duration)

        # 5. Add Teaser if provided
        if teaser_text:
            teaser_clip = self._make_teaser_clip(teaser_text)
            final = concatenate_videoclips([main_video, teaser_clip])
        else:
            final = main_video

        # 6. Write output
        output_path = os.path.join(self.output_dir, output_filename)
        final.write_videofile(
            output_path,
            fps=self.FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate="12M",
            preset="slow",
            logger=None,
        )

        # Cleanup
        for c in audio_clips:
            c.close()
        combined_audio.close()
        bg_video.close()
        final.close()

        return output_path
