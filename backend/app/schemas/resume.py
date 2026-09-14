"""Resume Parsing and Extraction Pydantic Schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    """Schema returned immediately upon file upload and text extraction."""
    id: int
    filename: str
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    file_url: Optional[str] = None
    parsed_skills: List[str] = []
    experience_years: float = 0.0
    education_level: Optional[str] = None
    uploaded_at: datetime
    message: str = "Resume successfully parsed and ingested"

    class Config:
        from_attributes = True


class ResumeDetailResponse(BaseModel):
    """Detailed schema for inspected candidate resume records."""
    id: int
    candidate_id: Optional[int] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    filename: str
    file_url: Optional[str] = None
    raw_text: Optional[str] = None
    parsed_skills: List[str] = []
    experience_years: float = 0.0
    education_level: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True
