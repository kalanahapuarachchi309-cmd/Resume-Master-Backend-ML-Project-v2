"""Word DOCX Document Parser."""
class DOCXParser:
    @staticmethod
    def validate_file(file_bytes: bytes) -> bool:
        return file_bytes.startswith(b"PK")
