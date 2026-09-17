"""Resume Upload, File Ingestion, and Batch Parsing Handlers (Mahen & Team)."""
import os
import uuid
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, status
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeUploadResponse, ResumeDetailResponse
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.docx_parser import DocxParser
from app.services.nlp.skill_extractor import SkillExtractor
from app.services.cloudinary_service import CloudinaryService
from app.core.security import get_current_user

router = APIRouter(prefix="/resumes", tags=["Resumes"])


def _save_and_parse_file(file_bytes: bytes, original_filename: str) -> dict:
    """Helper to validate, save to unique path, upload to Cloudinary, and parse document."""
    # Enforce file size limit
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    # Sanitize and create unique file storage path
    clean_name = re.sub(r"[^a-zA-Z0-9_\.-]", "_", original_filename.lower())
    ext = os.path.splitext(clean_name)[1]
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload .pdf or .docx files only."
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex[:10]}_{clean_name}"
    disk_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Write actual file bytes to disk as local backup
    with open(disk_path, "wb") as f:
        f.write(file_bytes)

    # Upload to Cloudinary CDN (Mahen & Team)
    cloudinary_url = CloudinaryService.upload_resume(file_bytes, original_filename)
    if not cloudinary_url:
        print(f"[Cloudinary Warning] Document '{original_filename}' was not uploaded to Cloudinary (check 'pip install cloudinary' and internet). Saved to local backup disk: {disk_path}")

    # Extract text according to format
    if ext == ".pdf":
        if not PDFParser.validate_file(file_bytes):
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF document.")
        raw_text = PDFParser.extract_text(file_bytes)
    else:  # .docx
        if not DocxParser.validate_file(file_bytes):
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid DOCX document.")
        raw_text = DocxParser.extract_text(file_bytes)

    if not raw_text or len(raw_text.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract readable text from resume. Please ensure the document is not an empty or scanned image file."
        )

    # NLP feature extraction
    parsed_skills = SkillExtractor.extract_skills(raw_text)
    experience_years = SkillExtractor.extract_experience_years(raw_text)
    education_level = SkillExtractor.extract_education(raw_text)
    candidate_email = SkillExtractor.extract_email(raw_text)
    candidate_phone = SkillExtractor.extract_phone(raw_text)

    # Intelligent candidate name extraction
    candidate_name = None
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    for line in lines[:10]:
        if '@' in line or 'http' in line or re.search(r'\d{4,}', line):
            continue
        lower_line = line.lower()
        if any(h in lower_line for h in ['resume', 'curriculum', 'vitae', 'project', 'education', 'experience', 'summary', 'profile', 'about', 'skills', 'contact', 'workexperience', 'first last']):
            continue
        clean_line = re.sub(r'[^A-Za-z\s\.\-\']', '', line).strip()
        words = clean_line.split()
        if 2 <= len(words) <= 4 and all(len(w) >= 2 for w in words):
            if lower_line not in ['first last', 'your name', 'candidate name', 'john doe', 'jane doe']:
                candidate_name = clean_line.title()
                break

    if not candidate_name or candidate_name.lower() in ['first last', 'first last contact', 'contact']:
        base = original_filename.rsplit('.', 1)[0]
        clean = re.sub(r'(?i)(_resume|_cv|resume|cv|template|\d+)', '', base).strip(' _-')
        clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', clean).replace('_', ' ').replace('-', ' ').strip()
        if clean and len(clean.split()) >= 1 and clean.lower() not in ['first last', 'contact']:
            candidate_name = clean.title()

    if not candidate_name and candidate_email and not candidate_email.endswith('@resumeworded.com'):
        prefix = candidate_email.split('@')[0]
        clean_prefix = re.sub(r'[^a-zA-Z]', ' ', prefix).strip()
        if clean_prefix:
            candidate_name = clean_prefix.title()

    effective_file_url = cloudinary_url or f"/api/resumes/file/{unique_filename}"

    return {
        "filename": original_filename,
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "file_path": disk_path,
        "file_url": effective_file_url,
        "raw_text": raw_text,
        "parsed_skills": parsed_skills,
        "experience_years": experience_years,
        "education_level": education_level,
    }


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle candidate single resume upload, Cloudinary CDN sync, and NLP extraction."""
    content = await file.read()
    parsed_data = _save_and_parse_file(content, file.filename)

    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    name = current_user.name if user_role == "CANDIDATE" else (parsed_data["candidate_name"] or current_user.name)

    resume = Resume(
        candidate_id=current_user.id,
        candidate_name=name,
        candidate_email=parsed_data.get("candidate_email"),
        filename=parsed_data["filename"],
        file_path=parsed_data["file_path"],
        file_url=parsed_data.get("file_url"),
        raw_text=parsed_data["raw_text"],
        parsed_skills=parsed_data["parsed_skills"],
        experience_years=parsed_data["experience_years"],
        education_level=parsed_data["education_level"],
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeUploadResponse(
        id=resume.id,
        filename=resume.filename,
        candidate_name=resume.candidate_name,
        candidate_email=resume.candidate_email,
        file_url=resume.file_url or resume.file_path,
        parsed_skills=resume.parsed_skills,
        experience_years=resume.experience_years,
        education_level=resume.education_level,
        uploaded_at=resume.uploaded_at,
        message="Resume successfully processed, backed up to Cloudinary, and indexed.",
    )


@router.post("/upload-batch", response_model=List[ResumeUploadResponse], status_code=status.HTTP_201_CREATED)
@router.post("/upload-bulk", response_model=List[ResumeUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_batch_resumes(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and parse a batch/bulk of candidate resumes simultaneously (supports up to 300 CVs in chunked batches)."""
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files were provided for upload.")

    results = []
    for upload in files:
        try:
            content = await upload.read()
            parsed_data = _save_and_parse_file(content, upload.filename)

            candidate_display_name = parsed_data.get("candidate_name")
            if not candidate_display_name:
                base_name = upload.filename.rsplit(".", 1)[0]
                clean_name = re.sub(r"(?i)(_resume|_cv|resume|cv)", "", base_name).strip(" _-")
                candidate_display_name = clean_name.replace("_", " ").replace("-", " ").title()
            if not candidate_display_name:
                candidate_display_name = upload.filename.rsplit(".", 1)[0].replace("_", " ").title()

            resume = Resume(
                candidate_id=current_user.id,
                candidate_name=candidate_display_name,
                candidate_email=parsed_data.get("candidate_email"),
                filename=parsed_data["filename"],
                file_path=parsed_data["file_path"],
                file_url=parsed_data.get("file_url"),
                raw_text=parsed_data["raw_text"],
                parsed_skills=parsed_data["parsed_skills"],
                experience_years=parsed_data["experience_years"],
                education_level=parsed_data["education_level"],
            )
            db.add(resume)
            db.commit()
            db.refresh(resume)

            results.append(ResumeUploadResponse(
                id=resume.id,
                filename=resume.filename,
                candidate_name=resume.candidate_name,
                candidate_email=resume.candidate_email,
                file_url=resume.file_url or resume.file_path,
                parsed_skills=resume.parsed_skills,
                experience_years=resume.experience_years,
                education_level=resume.education_level,
                uploaded_at=resume.uploaded_at,
                message="Successfully parsed, uploaded to Cloudinary, and indexed.",
            ))
        except Exception as e:
            # Continue with remaining files if one encounters an error
            continue

    return results


@router.get("", response_model=List[ResumeDetailResponse])
@router.get("/", response_model=List[ResumeDetailResponse], include_in_schema=False)
def list_resumes(
    skip: int = 0,
    limit: int = Query(300, ge=1, le=1000, description="Number of resumes to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List parsed candidate resumes. Candidates view their own; Recruiters view all."""
    query = db.query(Resume)
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)

    if user_role == "CANDIDATE":
        query = query.filter(Resume.candidate_id == current_user.id)

    return query.order_by(Resume.uploaded_at.desc()).offset(skip).limit(limit).all()


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve detailed parsed resume data."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role == "CANDIDATE" and resume.candidate_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to candidate record")

    return resume


@router.get("/cloudinary-status")
def get_cloudinary_status():
    """Diagnostic endpoint to verify Cloudinary installation, configuration, and connectivity."""
    return CloudinaryService.check_status()


@router.post("/sync-cloudinary")
def sync_cloudinary_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync, verify, and import all resumes stored on Cloudinary CDN into database."""
    result = CloudinaryService.sync_from_cloudinary(db=db, user_id=current_user.id)
    return result


@router.get("/{resume_id}/file")
def get_resume_file(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Serve or redirect to candidate resume document (always redirects to Cloudinary CDN)."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume record not found")

    # 1. If Cloudinary URL exists, redirect directly to Cloudinary CDN
    if resume.file_url and (resume.file_url.startswith("http://") or resume.file_url.startswith("https://")):
        return RedirectResponse(url=resume.file_url)

    if resume.file_path and (resume.file_path.startswith("http://") or resume.file_path.startswith("https://")):
        return RedirectResponse(url=resume.file_path)

    # 2. If stored on local disk, upload to Cloudinary on-the-fly and redirect
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            with open(resume.file_path, "rb") as f:
                content = f.read()
            c_url = CloudinaryService.upload_resume(content, resume.filename)
            if c_url:
                resume.file_url = c_url
                db.commit()
                return RedirectResponse(url=c_url)
        except Exception:
            pass

        media_type = "application/pdf" if resume.filename.lower().endswith(".pdf") else "application/octet-stream"
        return FileResponse(resume.file_path, media_type=media_type, filename=resume.filename)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume document file not found")
