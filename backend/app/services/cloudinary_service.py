"""Cloudinary Cloud Storage Integration Service (Mahen & Team)."""
import os
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    _has_cloudinary = True
except ImportError:
    _has_cloudinary = False

from app.core.config import settings


class CloudinaryService:
    """Uploads and manages resume documents in Cloudinary CDN."""

    _initialized = False

    @classmethod
    def _init_cloudinary(cls):
        """Initialize Cloudinary client with credentials."""
        if not cls._initialized and _has_cloudinary:
            if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                    api_key=settings.CLOUDINARY_API_KEY,
                    api_secret=settings.CLOUDINARY_API_SECRET,
                    secure=True,
                )
                cls._initialized = True
                logger.info(f"Cloudinary successfully configured for cloud: {settings.CLOUDINARY_CLOUD_NAME}")

    @classmethod
    def check_status(cls) -> dict:
        """Run diagnostics on Cloudinary SDK, configuration, and connectivity."""
        if not _has_cloudinary:
            return {
                "ok": False,
                "installed": False,
                "error": "The 'cloudinary' Python package is not installed in this environment. Run: pip install cloudinary>=1.40.0"
            }

        if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET):
            return {
                "ok": False,
                "installed": True,
                "configured": False,
                "error": "Cloudinary credentials missing in settings/env (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)."
            }

        cls._init_cloudinary()

        try:
            ping_res = cloudinary.api.ping()
            return {
                "ok": True,
                "installed": True,
                "configured": True,
                "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
                "folder": settings.CLOUDINARY_FOLDER,
                "ping": ping_res,
                "message": "Cloudinary is fully connected and ready for uploads."
            }
        except Exception as e:
            return {
                "ok": False,
                "installed": True,
                "configured": True,
                "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
                "error": f"Failed to connect to Cloudinary API: {str(e)}"
            }

    @classmethod
    def upload_resume(cls, file_bytes: bytes, filename: str) -> Optional[str]:
        """Upload resume bytes to Cloudinary raw storage and return secure HTTPS URL."""
        if not _has_cloudinary:
            print("[Cloudinary Error] 'cloudinary' package is not installed! Run: pip install cloudinary")
            return None
        if not file_bytes:
            return None

        cls._init_cloudinary()

        try:
            # Generate safe public_id with unique prefix to avoid collision while retaining readable filename
            clean_name = os.path.splitext(filename)[0]
            clean_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in clean_name).strip("_")
            public_id = f"{clean_name}_{uuid.uuid4().hex[:8]}"

            folder = settings.CLOUDINARY_FOLDER or "resume_master"

            upload_result = cloudinary.uploader.upload(
                file_bytes,
                resource_type="raw",
                folder=folder,
                public_id=public_id,
                overwrite=True,
            )

            secure_url = upload_result.get("secure_url") or upload_result.get("url")
            logger.info(f"Uploaded resume '{filename}' to Cloudinary: {secure_url}")
            return secure_url
        except Exception as e:
            print(f"[Cloudinary Upload Error] Failed to upload '{filename}': {e}")
            logger.error(f"Cloudinary upload failed for '{filename}': {e}")
            return None

    @classmethod
    def list_resumes(cls, max_results: int = 500) -> list:
        """List all resume resources stored in Cloudinary folder."""
        if not _has_cloudinary:
            return []
        cls._init_cloudinary()
        folder = settings.CLOUDINARY_FOLDER or "resume_master"
        try:
            res = cloudinary.api.resources(
                type="upload",
                resource_type="raw",
                prefix=folder,
                max_results=max_results,
            )
            return res.get("resources", [])
        except Exception as e:
            logger.error(f"Failed to list Cloudinary resources: {e}")
            return []

    @classmethod
    def download_resume_bytes(cls, url: str) -> Optional[bytes]:
        """Download resume document bytes directly from Cloudinary CDN URL."""
        import httpx
        try:
            resp = httpx.get(url, follow_redirects=True, timeout=30.0)
            if resp.status_code == 200:
                return resp.content
            return None
        except Exception as e:
            logger.error(f"Failed to download resume from Cloudinary URL {url}: {e}")
            return None

    @classmethod
    def sync_missing_to_cloudinary(cls, db) -> int:
        """Upload any existing resumes without Cloudinary CDN URLs directly to Cloudinary."""
        from app.models.resume import Resume

        missing_resumes = (
            db.query(Resume)
            .filter((Resume.file_url == None) | (~Resume.file_url.startswith("http")))
            .all()
        )
        updated_count = 0
        for r in missing_resumes:
            if r.file_path and os.path.exists(r.file_path):
                try:
                    with open(r.file_path, "rb") as f:
                        file_bytes = f.read()
                    cloud_url = cls.upload_resume(file_bytes, r.filename)
                    if cloud_url:
                        r.file_url = cloud_url
                        updated_count += 1
                except Exception as e:
                    logger.error(f"Failed to upload local file for resume #{r.id}: {e}")
        if updated_count > 0:
            db.commit()
        return updated_count

    @classmethod
    def sync_from_cloudinary(cls, db, user_id: Optional[int] = None) -> dict:
        """Sync and import any resumes stored on Cloudinary into the database."""
        from app.models.resume import Resume
        from app.services.parsers.pdf_parser import PDFParser
        from app.services.parsers.docx_parser import DocxParser
        from app.services.nlp.skill_extractor import SkillExtractor
        import re

        # 1. First ensure any local resumes have Cloudinary URLs
        local_uploaded = cls.sync_missing_to_cloudinary(db)

        # 2. Query Cloudinary CDN resources
        resources = cls.list_resumes(max_results=500)
        existing_urls = {
            r[0] for r in db.query(Resume.file_url).filter(Resume.file_url != None).all()
        }

        imported_count = 0
        for item in resources:
            secure_url = item.get("secure_url") or item.get("url")
            if not secure_url or secure_url in existing_urls:
                continue

            # Download document from Cloudinary CDN
            file_bytes = cls.download_resume_bytes(secure_url)
            if not file_bytes:
                continue

            public_id = item.get("public_id", "")
            raw_filename = public_id.split("/")[-1]
            ext = os.path.splitext(raw_filename)[1].lower()
            if not ext:
                ext = ".pdf"
                raw_filename += ".pdf"

            try:
                if ext == ".pdf":
                    raw_text = PDFParser.extract_text(file_bytes) if PDFParser.validate_file(file_bytes) else ""
                else:
                    raw_text = DocxParser.extract_text(file_bytes) if DocxParser.validate_file(file_bytes) else ""

                skills = SkillExtractor.extract_skills(raw_text)
                exp_years = SkillExtractor.extract_experience_years(raw_text)
                edu_level = SkillExtractor.extract_education(raw_text)
                cand_email = SkillExtractor.extract_email(raw_text)

                base_name = raw_filename.rsplit(".", 1)[0]
                clean_name = re.sub(r"(?i)(_resume|_cv|resume|cv)", "", base_name).strip(" _-")
                cand_name = clean_name.replace("_", " ").replace("-", " ").title()
                if not cand_name:
                    cand_name = raw_filename.rsplit(".", 1)[0].title()

                resume = Resume(
                    candidate_id=user_id,
                    candidate_name=cand_name,
                    candidate_email=cand_email,
                    filename=raw_filename,
                    file_path=secure_url,
                    file_url=secure_url,
                    raw_text=raw_text,
                    parsed_skills=skills,
                    experience_years=exp_years,
                    education_level=edu_level,
                )
                db.add(resume)
                db.commit()
                db.refresh(resume)
                existing_urls.add(secure_url)
                imported_count += 1
            except Exception as e:
                logger.error(f"Failed to import Cloudinary resource {secure_url}: {e}")
                continue

        total_resumes = db.query(Resume).count()
        return {
            "status": "success",
            "local_synced_to_cloudinary": local_uploaded,
            "newly_imported_from_cloudinary": imported_count,
            "total_cloudinary_resumes_in_db": total_resumes,
            "total_resources_in_cloudinary": len(resources),
        }
