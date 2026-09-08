"""API Route Controllers Package."""
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.jobs import router as jobs_router
from app.routes.resumes import router as resumes_router
from app.routes.matching import router as matching_router

__all__ = [
    "auth_router",
    "users_router",
    "jobs_router",
    "resumes_router",
    "matching_router",
]
