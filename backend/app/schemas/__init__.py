"""Pydantic DTO Schemas Package."""
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserProfile
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.schemas.resume import ResumeUploadResponse, ResumeDetailResponse
from app.schemas.matching import MatchEvaluationRequest, CandidateMatchDetail, JobMatchingResponse

__all__ = [
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "UserProfile",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "ResumeUploadResponse",
    "ResumeDetailResponse",
    "MatchEvaluationRequest",
    "CandidateMatchDetail",
    "JobMatchingResponse",
]
