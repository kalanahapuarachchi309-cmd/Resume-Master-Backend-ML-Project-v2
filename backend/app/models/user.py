"""User Model & Role Enum."""
import enum
from sqlalchemy import Column, Integer, String, Enum
from app.database.base import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    RECRUITER = "RECRUITER"
    CANDIDATE = "CANDIDATE"
