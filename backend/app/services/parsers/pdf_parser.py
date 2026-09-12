"""PDF Document Parser Service (Mahen & Team)."""
import io
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PDFParser:
    """Extracts clean text content from PDF resume files using pdfplumber / pypdf."""

    @staticmethod
    def validate_file(file_bytes: bytes) -> bool:
        """Verify that the byte stream has a valid PDF magic number header."""
        return file_bytes.startswith(b"%PDF")

    @classmethod
    def _normalize_spaced_text(cls, text: str) -> str:
        """De-spaces text from PDFs with tracked font kerning or spaced letterforms."""
        if not text:
            return ""
        lines = []
        for line in text.split('\n'):
            tokens = line.split(' ')
            single_chars = [t for t in tokens if len(t) == 1]
            if len(tokens) > 4 and len(single_chars) / len(tokens) > 0.35:
                words = re.split(r'  +', line)
                new_words = []
                for w in words:
                    cleaned_word = re.sub(r'(?<=\S) (?=\S)', '', w)
                    new_words.append(cleaned_word)
                lines.append(' '.join(new_words))
            else:
                lines.append(line)
        return '\n'.join(lines)

    @classmethod
    def extract_text(cls, file_bytes: bytes) -> str:
        """Extract multi-column text from PDF raw bytes while preserving reading structure."""
        if not file_bytes:
            return ""

        extracted_pages = []

        # 1. Try pdfplumber first (best for multi-column resumes)
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        extracted_pages.append(text.strip())
            if extracted_pages:
                full_text = "\n\n".join(extracted_pages)
                return cls._normalize_spaced_text(full_text)
        except Exception as e:
            logger.debug(f"pdfplumber extraction skipped or failed: {e}")

        # 2. Fallback to pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    extracted_pages.append(text.strip())
            if extracted_pages:
                full_text = "\n\n".join(extracted_pages)
                return cls._normalize_spaced_text(full_text)
        except Exception as e:
            logger.error(f"pypdf extraction error: {e}")

        return ""
