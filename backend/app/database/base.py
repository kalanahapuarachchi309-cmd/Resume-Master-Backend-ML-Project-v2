"""Centralized declarative base importing all models for migrations."""
from app.database.connection import Base
from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app.models.match_result import MatchResult

__all__ = ["Base", "User", "Job", "Resume", "MatchResult"]
