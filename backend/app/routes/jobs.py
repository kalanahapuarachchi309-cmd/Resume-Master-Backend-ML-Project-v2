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


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(require_role(["RECRUITER", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """Create a new job posting (Recruiter or Admin only)."""
    return JobService.create_job(db=db, job_in=job_in, recruiter_id=current_user.id)


@router.get("", response_model=List[JobResponse])
@router.get("/", response_model=List[JobResponse], include_in_schema=False)
def list_jobs(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = Query(None, description="Search keyword in title, description, or location"),
    db: Session = Depends(get_db),
):
    """List available jobs with optional keyword filtering and pagination."""
    return JobService.list_jobs(db=db, skip=skip, limit=limit, search=search)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed specifications for a specific job."""
    job = JobService.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: User = Depends(require_role(["RECRUITER", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """Update existing job requirements (Job creator or Admin)."""
    job = JobService.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if job.recruiter_id != current_user.id and user_role not in ["ADMIN", "RECRUITER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this job posting"
        )

    updated_job = JobService.update_job(db=db, job_id=job_id, job_update=job_update)
    return updated_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    current_user: User = Depends(require_role(["RECRUITER", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """Remove a job listing (Job creator, Recruiter, or Admin)."""
    job = JobService.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if job.recruiter_id != current_user.id and user_role not in ["ADMIN", "RECRUITER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this job posting"
        )

    JobService.delete_job(db=db, job_id=job_id)
    return None
