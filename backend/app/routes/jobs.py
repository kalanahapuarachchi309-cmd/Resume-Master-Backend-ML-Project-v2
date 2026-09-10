"""Job Management Route Handlers (Kalana)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.services.job_service import JobService
from app.core.security import require_role

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(require_role(["RECRUITER", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """Create a new job posting (Recruiter or Admin only)."""
    return JobService.create_job(db=db, job_in=job_in, recruiter_id=current_user.id)


