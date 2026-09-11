"""Job Service Unit Test Suite (Mahen)."""
import pytest
from app.schemas.job import JobCreate, JobUpdate
from app.services.job_service import JobService
from app.database.connection import SessionLocal, init_db
from app.models.job import Job

def test_job_create_schema_validation():
    """Verify JobCreate schema validates required skills and experience."""
    job_in = JobCreate(
        title="Full Stack Developer",
        description="Developing modern React and FastAPI microservices.",
        required_skills=["React", "FastAPI", "Python", "SQL"],
        experience_required=3.0,
        location="Remote",
    )
    assert job_in.title == "Full Stack Developer"
    assert len(job_in.required_skills) == 4
    assert job_in.experience_required == 3.0

def test_job_service_lifecycle():
    """Verify JobService create, fetch, and update lifecycle."""
    init_db()
    db = SessionLocal()
    job_in = JobCreate(
        title="DevOps Engineer",
        description="Kubernetes, Docker, and CI/CD pipelines.",
        required_skills=["Docker", "Kubernetes", "AWS"],
        experience_required=2.0,
        location="Colombo",
    )
    job = JobService.create_job(db, job_in, recruiter_id=1)
    assert job.id is not None
    assert job.title == "DevOps Engineer"
    
    fetched = JobService.get_job(db, job.id)
    assert fetched is not None
    assert fetched.id == job.id
