"""Document Parsers Package for PDF and DOCX."""
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.docx_parser import DocxParser

__all__ = ["PDFParser", "DocxParser"]
