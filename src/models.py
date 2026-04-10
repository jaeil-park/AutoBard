from pydantic import BaseModel
from typing import Literal, Optional, Dict

class TextSegment(BaseModel):
    text: str
    type: Literal["narrative", "dialogue"]
    meta: Optional[Dict] = None

    def __str__(self):
        icon = "🗨️" if self.type == "dialogue" else "📝"
        return f"[{icon} {self.type.upper()}] {self.text}"
