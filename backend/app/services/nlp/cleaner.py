"""Text Cleaning Pipeline."""
import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        if not text: return ""
        return re.sub(r"\s+", " ", text).strip().lower()
