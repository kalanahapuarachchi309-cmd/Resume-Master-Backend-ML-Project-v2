"""FastAPI Application Entrypoint (Full-Stack Backend)."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.connection import init_db
from app.ml.predictor import predictor_service
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.jobs import router as jobs_router
from app.routes.resumes import router as resumes_router
from app.routes.matching import router as matching_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: automatically initialize database tables & ML artifacts on boot."""
    # 1. Initialize relational database tables
    init_db()

    # 2. Ensure uploads directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 3. Preload ML predictor artifacts
    predictor_service.load_model()

    # 4. Automatically sync candidate resumes from Cloudinary CDN on boot (in background thread)
    import threading

    def _bg_sync():
        try:
            from app.database.connection import SessionLocal
            from app.services.cloudinary_service import CloudinaryService
            db = SessionLocal()
            CloudinaryService.sync_from_cloudinary(db)
            db.close()
        except Exception:
            pass

    threading.Thread(target=_bg_sync, daemon=True).start()

    yield


# Initialize FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="Production ML-Powered Resume Screening & Candidate Ranking REST API",
    version="2.0.0",
    lifespan=lifespan,
)

# Global Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under standard prefix
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(resumes_router, prefix=settings.API_V1_STR)
app.include_router(matching_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["System"])
async def root():
    """Application root index."""
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Comprehensive system healthcheck reporting DB, ML Model, and API status."""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_model_loaded": predictor_service.is_ready,
        "ml_model_name": predictor_service.model_name,
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB,
    }
