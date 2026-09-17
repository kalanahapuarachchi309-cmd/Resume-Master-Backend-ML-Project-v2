"""Job-Resume Match Result Database ORM Model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base


class MatchResult(Base):
    """MatchResult table storing evaluated candidate rankings and explainable scores."""
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, nullable=False)  # 0.0 to 100.0%
    rank = Column(Integer, nullable=True)        # Leaderboard ranking position
    matched_skills = Column(JSON, nullable=False, default=list)
    missing_skills = Column(JSON, nullable=False, default=list)
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="match_results")
    resume = relationship("Resume", back_populates="match_results")
