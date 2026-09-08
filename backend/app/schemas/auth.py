from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from app.models.user import UserRole


class UserRegister(BaseModel):
    """Schema for registering a new user."""
    email: EmailStr = Field(..., description="Unique email address")
    name: str = Field(..., min_length=2, max_length=100, description="Full candidate or recruiter name")
    password: str = Field(..., min_length=6, max_length=128, description="User password (min 6 characters)")
    role: UserRole = Field(default=UserRole.CANDIDATE, description="User access control role")

    @model_validator(mode="before")
    @classmethod
    def handle_name_aliases(cls, data: Any) -> Any:
        """Allow 'full_name' or 'name' interchangeably."""
        if isinstance(data, dict):
            if "name" not in data and "full_name" in data:
                data["name"] = data["full_name"]
            elif "full_name" not in data and "name" in data:
                data["full_name"] = data["name"]
        return data


class UserLogin(BaseModel):
    """Schema for user credential validation."""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Public user profile response schema."""
    id: int
    email: EmailStr
    name: str
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for JWT access token response."""
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user: Optional[UserProfile] = None


class TokenPayload(BaseModel):
    """Decoded token payload schema."""
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
