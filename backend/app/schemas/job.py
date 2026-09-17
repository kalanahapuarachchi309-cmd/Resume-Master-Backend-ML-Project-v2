from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class JobBase(BaseModel):
    """Base schema for job properties."""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    required_skills: List[str] = Field(default_factory=list)
    experience_required: float = Field(default=0.0, ge=0.0)
    min_experience_years: Optional[float] = None
    education_level: Optional[str] = "Bachelor's Degree"
    location: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def handle_job_aliases(cls, data: Any) -> Any:
        def parse_skills(val: Any) -> List[str]:
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                import json
                try:
                    p = json.loads(val)
                    if isinstance(p, list):
                        return p
                except Exception:
                    pass
                return [s.strip() for s in val.split(",") if s.strip()]
            return []

        if isinstance(data, dict):
            if "experience_required" not in data and "min_experience_years" in data:
                data["experience_required"] = float(data["min_experience_years"])
            elif "min_experience_years" not in data and "experience_required" in data:
                data["min_experience_years"] = float(data["experience_required"])
            if "required_skills" in data and data["required_skills"] is not None:
                data["required_skills"] = parse_skills(data["required_skills"])
        elif hasattr(data, "experience_required"):
            if not getattr(data, "min_experience_years", None):
                setattr(data, "min_experience_years", data.experience_required)
            skills = getattr(data, "required_skills", None)
            setattr(data, "required_skills", parse_skills(skills))
        return data


class JobCreate(JobBase):
    """Schema for creating a new job posting."""
    pass


class JobUpdate(BaseModel):
    """Schema for updating an existing job posting."""
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_required: Optional[float] = None
    min_experience_years: Optional[float] = None
    education_level: Optional[str] = None
    location: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def handle_job_aliases(cls, data: Any) -> Any:
        def parse_skills(val: Any) -> List[str]:
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                import json
                try:
                    p = json.loads(val)
                    if isinstance(p, list):
                        return p
                except Exception:
                    pass
                return [s.strip() for s in val.split(",") if s.strip()]
            return []

        if isinstance(data, dict):
            if "experience_required" not in data and "min_experience_years" in data:
                data["experience_required"] = float(data["min_experience_years"])
            elif "min_experience_years" not in data and "experience_required" in data:
                data["min_experience_years"] = float(data["experience_required"])
            if "required_skills" in data and data["required_skills"] is not None:
                data["required_skills"] = parse_skills(data["required_skills"])
        elif hasattr(data, "experience_required"):
            if not getattr(data, "min_experience_years", None):
                setattr(data, "min_experience_years", data.experience_required)
            skills = getattr(data, "required_skills", None)
            if skills is not None:
                setattr(data, "required_skills", parse_skills(skills))
        return data


class JobResponse(JobBase):
    """Schema for serializing a job posting in API responses."""
    id: int
    recruiter_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
