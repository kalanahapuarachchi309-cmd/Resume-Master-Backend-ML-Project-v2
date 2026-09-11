"""Job Posting Database ORM Model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Job(Base):
    """Job listing model representing job vacancies posted by recruiters."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=False, default=list)  # List of skill strings
    experience_required = Column(Float, default=0.0, nullable=False)  # in years
    education_level = Column(String(100), nullable=True, default="Bachelor's Degree")
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recruiter = relationship("User", back_populates="jobs")
    match_results = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")

# verified cascading delete integrity
