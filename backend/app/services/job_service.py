"""Job Management Service Layer (Kalana)."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    """Service handling job database queries and business logic."""

    @staticmethod
    def get_job(db: Session, job_id: int) -> Optional[Job]:
        """Fetch a job posting by its primary key ID."""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def list_jobs(db: Session, skip: int = 0, limit: int = 50, search: Optional[str] = None) -> List[Job]:
        """List job postings with optional keyword search and pagination."""
        query = db.query(Job)
        if search and search.strip():
            keyword = f"%{search.strip()}%"
            query = query.filter(
                (Job.title.ilike(keyword)) | 
                (Job.description.ilike(keyword)) |
                (Job.location.ilike(keyword))
            )
        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    