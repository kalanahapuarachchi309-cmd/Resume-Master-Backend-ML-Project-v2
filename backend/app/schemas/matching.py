"""Candidate Evaluation and Job Matching Pydantic Schemas."""
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator


class MatchEvaluationRequest(BaseModel):
    """Payload to trigger matching evaluation for a specific job."""
    job_id: int
    resume_ids: Optional[List[int]] = None  # None evaluates all available resumes


class CandidateMatchDetail(BaseModel):
    """Granular explainable match result for an individual candidate."""
    resume_id: int
    candidate_name: str
    candidate_email: Optional[str] = None
    match_score: float = Field(..., ge=0.0, le=100.0, description="Percentage match score")
    overall_score: Optional[float] = None
    rank: int
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    candidate_skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    experience_fit: str = "N/A"
    education_level: Optional[str] = None
    education_fit: Optional[str] = None
    match_summary: Optional[str] = None
    model_used: Optional[str] = "RandomForestClassifier (Supervised ML)"
    feature_contributions: Optional[dict] = None
    file_url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_score_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "overall_score" not in data and "match_score" in data:
                data["overall_score"] = data["match_score"]
            elif "match_score" not in data and "overall_score" in data:
                data["match_score"] = data["overall_score"]
        elif hasattr(data, "match_score") and not hasattr(data, "overall_score"):
            setattr(data, "overall_score", data.match_score)
        return data


class JobMatchingResponse(BaseModel):
    """Leaderboard summary response for a matched job posting."""
    job_id: int
    job_title: str
    total_candidates_evaluated: int
    evaluated_at: datetime
    rankings: List[CandidateMatchDetail]
