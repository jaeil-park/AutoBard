import re
from typing import List
from .models import TextSegment

class TextPreprocessor:
    def __init__(self):
        # Regex to find quoted text (dialogue)
        # Using [^"]* to capture everything inside double quotes
        self.dialogue_pattern = re.compile(r'("[^"]*")')

    def split_text(self, text: str) -> List[TextSegment]:
        """
        Splits text into narrative and dialogue segments.
        """
        if not text:
            return []

        # Remove unnecessary leading/trailing whitespace but keep inner flow
        text = text.strip()
        
        segments = []
        
        # We use re.split with a capturing group to keep the delimiters (the quotes)
        # This gives us a list where every odd element (index 1, 3, 5...) is a dialogue
        parts = self.dialogue_pattern.split(text)
        
        for i, part in enumerate(parts):
            if not part.strip():
                continue
                
            is_dialogue = i % 2 != 0
            seg_type = "dialogue" if is_dialogue else "narrative"
            
            # Clean up the text: if it's dialogue, it might have the quotes included
            # If it's narrative, just strip whitespace
            clean_text = part.strip()
            
            segments.append(TextSegment(
                text=clean_text,
                type=seg_type
            ))
            
        return segments

    def process_story(self, raw_text: str) -> List[TextSegment]:
        """
        Processes a full story text, handling line breaks and multiple paragraphs.
        """
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        all_segments = []
        
        for line in lines:
            line_segments = self.split_text(line)
            all_segments.extend(line_segments)
            
        return all_segments
