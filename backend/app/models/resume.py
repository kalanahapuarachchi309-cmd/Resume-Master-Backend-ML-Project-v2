"""Resume Database ORM Model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Resume(Base):
    """Resume model storing parsed metadata and raw extracted text."""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    raw_text = Column(Text, nullable=True)
    parsed_skills = Column(JSON, nullable=False, default=list)  # List of extracted skills
    experience_years = Column(Float, default=0.0, nullable=False)
    education_level = Column(String(100), nullable=True)
    file_url = Column(String(512), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    candidate = relationship("User", back_populates="resumes")
    match_results = relationship("MatchResult", back_populates="resume", cascade="all, delete-orphan")
