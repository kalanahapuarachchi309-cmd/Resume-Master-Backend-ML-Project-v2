"""Text Preprocessing and Sanitization Service (Mahen & Team)."""
import re

STOPWORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "up", "about", "into", "over", "after", "is", "am", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "should", "can", "could", "this", "that", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
    "my", "your", "his", "their", "our"
}


class TextCleaner:
    """Preprocesses and sanitizes unstructured resume and job description text."""

    @staticmethod
    def clean(text: str) -> str:
        """Strip URLs, emails, phone numbers, special characters, and normalize whitespace."""
        if not text:
            return ""

        # Remove URLs
        text = re.sub(r"http\S+|www\S+|https\S+", " ", text, flags=re.MULTILINE)
        # Remove emails
        text = re.sub(r"\S+@\S+", " ", text)
        # Remove phone numbers
        text = re.sub(r"\+?\d[\d -]{8,}\d", " ", text)
        # Keep alphanumeric, +, # (for C++, C#) and spaces
        text = re.sub(r"[^a-zA-Z0-9\s\+\#]", " ", text)
        # Normalize multiple spaces and lowercase
        text = re.sub(r"\s+", " ", text).strip().lower()
        return text

    @classmethod
    def remove_stopwords(cls, text: str) -> str:
        """Filter out common English stopwords while preserving technical terms."""
        cleaned = cls.clean(text)
        if not cleaned:
            return ""

        words = cleaned.split()
        filtered = [w for w in words if w not in STOPWORDS and len(w) > 1]
        return " ".join(filtered)
