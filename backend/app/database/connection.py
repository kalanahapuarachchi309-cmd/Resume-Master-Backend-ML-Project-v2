"""Database Engine and Session Management (Kalana)."""
import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# Determine database engine with automatic SQLite fallback
database_url = settings.DATABASE_URL
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )
else:
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
    except Exception as e:
        logger.warning(f"Could not initialize PostgreSQL engine ({e}). Falling back to local SQLite.")
        fallback_url = "sqlite:///./resume_matcher.db"
        engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a scoped database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes all database tables, performs auto-migrations, and seeds default users."""
    import app.models  # Ensure all ORM models are registered with Base metadata
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

    # Auto-migration: ensure education_level column exists on jobs table
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if "jobs" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("jobs")]
            if "education_level" not in columns:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE jobs ADD COLUMN education_level VARCHAR(100) DEFAULT 'Bachelor''s Degree'"))
                logger.info("Auto-migrated 'jobs' table: added 'education_level' column.")

        if "resumes" in inspector.get_table_names():
            resumes_cols = [c["name"] for c in inspector.get_columns("resumes")]
            if "file_url" not in resumes_cols:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN file_url VARCHAR(512)"))
                logger.info("Auto-migrated 'resumes' table: added 'file_url' column.")
            if "candidate_email" not in resumes_cols:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN candidate_email VARCHAR(255)"))
                logger.info("Auto-migrated 'resumes' table: added 'candidate_email' column.")
    except Exception as e:
        logger.warning(f"Schema auto-migration notice: {e}")

    try:
        from app.database.seed import seed_default_users
        seed_default_users()
    except Exception as e:
        logger.warning(f"Could not auto-seed default users: {e}")
