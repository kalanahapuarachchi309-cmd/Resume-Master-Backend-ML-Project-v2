"""Job Management Service Layer."""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate

class JobService:
    @staticmethod
    def get_job(db: Session, job_id: int) -> Optional[Job]:
        return db.query(Job).filter(Job.id == job_id).first()
