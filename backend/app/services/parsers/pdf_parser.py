"""PDF Document Parsing Engine."""
class PDFParser:
    @staticmethod
    def validate_file(file_bytes: bytes) -> bool:
        return file_bytes.startswith(b"%PDF")
