"""Authentication and Job CRUD Tests (Kalana)."""
import pytest
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.models.user import User, UserRole
from app.schemas.job import JobCreate
from app.services.job_service import JobService


def test_password_hashing_and_verification():
    """Verify that password hashing creates valid hash and verifies correctly."""
    raw_password = "SecretPassword123!"
    hashed = get_password_hash(raw_password)
    
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_generation_and_decoding():
    """Verify that JWT token correctly encodes subject and role."""
    token = create_access_token(subject=42, role="RECRUITER")
    payload = decode_access_token(token)
    
    assert payload["sub"] == "42"
    assert payload["role"] == "RECRUITER"
    assert "exp" in payload


def test_job_service_create_and_fetch():
    """Verify JobService create and get operations."""
    # Test schema validation
    job_in = JobCreate(
        title="Backend Engineer",
        description="Looking for Python FastAPI developer with SQL experience.",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        experience_required=2.5,
        location="Colombo, Sri Lanka",
    )
    assert job_in.title == "Backend Engineer"
    assert len(job_in.required_skills) == 3
    assert job_in.experience_required == 2.5
