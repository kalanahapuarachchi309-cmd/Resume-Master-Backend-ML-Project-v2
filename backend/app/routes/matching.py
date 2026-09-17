"""ML Candidate Matching & Ranking Route Handlers (Sampath & Team)."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.matching import MatchEvaluationRequest, JobMatchingResponse
from app.services.ranking_service import RankingService
from app.core.security import require_role

router = APIRouter(prefix="/matching", tags=["Matching & Ranking"])


@router.post("/job/{job_id}/evaluate", response_model=JobMatchingResponse, status_code=status.HTTP_200_OK)
def evaluate_candidates_for_job(
    job_id: int,
    request: MatchEvaluationRequest,
    top_n: Optional[int] = Query(None, ge=1, le=500, description="Optionally limit top N candidates"),
    current_user=Depends(require_role(["RECRUITER", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """Trigger genuine ML feature extraction, model scoring, and ranking for candidates against a job."""
    try:
        return RankingService.evaluate_candidates(
            db=db,
            job_id=job_id,
            resume_ids=request.resume_ids,
            top_n=top_n
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ML Evaluation failed: {str(e)}")


@router.get("/job/{job_id}/rankings", response_model=JobMatchingResponse)
def get_job_rankings(
    job_id: int,
    top_n: Optional[int] = Query(None, ge=1, le=500, description="Optionally limit top N candidates"),
    current_user=Depends(require_role(["RECRUITER", "ADMIN"])),
    db: Session = Depends(get_db),
):
    """Retrieve saved ranking leaderboard and explainable match breakdown for a job."""
    try:
        return RankingService.get_job_rankings(db=db, job_id=job_id, top_n=top_n)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch rankings: {str(e)}")
