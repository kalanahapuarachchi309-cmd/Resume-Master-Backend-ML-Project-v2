# Complete Backend Testing & Postman Verification Guide

> **AI-Powered Resume/CV Screening & Job Matching System**  
> Complete technical reference, capabilities overview, local setup walkthrough, and Postman testing guide for team members, testers, and academic examiners.

---

## 1. What This Backend Can Do (Core Capabilities)

This system is an intelligent recruitment backend combining **FastAPI**, **SQLAlchemy**, and **Machine Learning** to automate the hiring and candidate evaluation workflow:

| Feature / Capability | Description |
| :--- | :--- |
| 🔐 **Authentication & RBAC** | Stateless JWT authentication with Bcrypt password hashing. Role-Based Access Control distinguishing `CANDIDATE`, `RECRUITER`, and `ADMIN`. |
| 📋 **Job Management CRUD** | Recruiters can post vacancies specifying job descriptions, mandatory skill tags (e.g. Python, FastAPI, Docker), and required years of experience. Candidates can browse and filter vacancies. |
| 📄 **Multi-Format Resume Ingestion** | Accepts uploaded candidate resumes in **PDF** and **Word (.docx)** formats. Files are validated, sanitized, and stored with unique UUID filenames to prevent collisions. |
| 🧠 **Intelligent NLP Parsing** | Cleans document text, extracts canonical technical skills using an alias normalization taxonomy (e.g. `JS` $\rightarrow$ `JavaScript`, `Postgres` $\rightarrow$ `PostgreSQL`), detects years of experience from phrasing & date spans, and classifies academic degrees. |
| ⚙️ **7 Feature Engineering Techniques** | Transforms unstructured resume and job texts into a uniform 7-dimensional numerical vector: TF-IDF cosine similarity, skill overlap ratio, skill count, missing skill ratio, experience delta, experience fit binary, and ordinal degree tier. |
| 🤖 **Trained ML Model Scoring** | Features are evaluated by a trained **Random Forest Classifier** (`F1 = 99.08%`), outputting a true probabilistic candidate suitability percentage ($0.0 - 100.0\%$). |
| 🏆 **Leaderboard & Explainability** | Ranks candidates strictly descending by ML score and generates an explainable breakdown: matched skills (green pills), missing required skills (red pills), and experience delta fitness. |

---

## 2. Technology Stack & Architectural Rationale

- **Web Framework:** `FastAPI` (Python 3.10+) — High performance, asynchronous endpoints, automatic Swagger UI documentation, and Pydantic v2 data validation.
- **Machine Learning & NLP:** `Scikit-Learn`, `Pandas`, `NumPy` — Feature vectorization, model training, and probabilistic inference.
- **Text Extraction:** `pdfplumber` & `pypdf` (for multi-column PDFs), `python-docx` & XML parsing (for DOCX).
- **ORM & Database:** `SQLAlchemy 2.0` — Relational schema mapping with automatic PostgreSQL connection and zero-configuration SQLite fallback for local testing.
- **Security & Cryptography:** `python-jose` (JWT), `passlib` & `hashlib` (Bcrypt / PBKDF2).
- **Testing:** `pytest` — Automated unit test suite.

---

## 3. Local Setup & Execution Guide for Testers

### Step 3.1: Clone & Setup Python Virtual Environment
Open PowerShell or your terminal in the project directory:

```powershell
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 3. Install required dependencies
pip install -r backend/requirements.txt
```

### Step 3.2: (Optional) Retrain ML Model & View Metrics
If you want to train the models from scratch and inspect the comparative accuracy table:

```powershell
python ml_pipeline/train_and_evaluate.py
```
*This compares Logistic Regression, SVM, and Random Forest, serializes `backend/app/ml/model.pkl`, and writes `ml_pipeline/EVALUATION_REPORT.md`.*

### Step 3.3: Launch the Backend Server
From the project root:

```powershell
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Once started, verify:
- **Interactive Swagger Documentation:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **System Health Check:** [`http://localhost:8000/health`](http://localhost:8000/health)

---

## 4. Step-by-Step Postman Testing Guide

You can test all endpoints using **Postman** (or your browser / cURL) by following this sequential workflow.

---

### Request 1: Health Check (Verify API & ML Model)
- **Method:** `GET`
- **URL:** `http://localhost:8000/health`
- **Expected Response (`200 OK`):**
```json
{
  "status": "healthy",
  "database": "connected",
  "ml_model_loaded": true,
  "ml_model_name": "RandomForestClassifier",
  "max_upload_size_mb": 10
}
```

---

### Request 2: Register a Recruiter Account
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/auth/register`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "email": "recruiter@techcorp.com",
  "name": "Sarah Jenkins",
  "password": "SecurePassword123!",
  "role": "RECRUITER"
}
```
- **Expected Response (`201 Created`):**
```json
{
  "id": 1,
  "email": "recruiter@techcorp.com",
  "name": "Sarah Jenkins",
  "role": "RECRUITER",
  "created_at": "2026-09-12T11:45:00.000000"
}
```

---

### Request 3: Login as Recruiter (Get Access Token)
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/auth/login`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "email": "recruiter@techcorp.com",
  "password": "SecurePassword123!"
}
```
- **Expected Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "RECRUITER"
}
```
> [!IMPORTANT]
> Copy the `access_token` string! You will use it in subsequent protected requests as `Authorization: Bearer <access_token>`.

---

### Request 4: Register & Login a Candidate Account
Repeat registration for a candidate:
- **POST** `http://localhost:8000/api/auth/register`
```json
{
  "email": "candidate.alex@gmail.com",
  "name": "Alex Johnson",
  "password": "CandidatePass123!",
  "role": "CANDIDATE"
}
```
- **POST** `http://localhost:8000/api/auth/login` to obtain Alex's candidate token.

---

### Request 5: Create a Job Vacancy (Recruiter Role Required)
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/jobs/`
- **Headers:** 
  - `Content-Type: application/json`
  - `Authorization: Bearer <recruiter_token>`
- **Body (raw JSON):**
```json
{
  "title": "Senior Python Backend Developer",
  "description": "We are seeking a Senior Python Developer with deep experience in FastAPI, PostgreSQL, Docker, Redis, and microservices architecture. Minimum 4 years of experience required with a Bachelor degree.",
  "required_skills": [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "Docker",
    "Redis",
    "REST API"
  ],
  "experience_required": 4.0,
  "location": "Colombo, Sri Lanka / Remote"
}
```
- **Expected Response (`201 Created`):**
```json
{
  "title": "Senior Python Backend Developer",
  "description": "We are seeking a Senior Python Developer...",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "REST API"],
  "experience_required": 4.0,
  "location": "Colombo, Sri Lanka / Remote",
  "id": 1,
  "recruiter_id": 1,
  "created_at": "2026-09-12T11:46:00.000000"
}
```

---

### Request 6: List Available Jobs
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/jobs/?search=Python`
- **Headers:** None required (Publicly viewable)
- **Expected Response (`200 OK`):** Returns array of job postings matching keyword query.

---

### Request 7: Upload and Parse a Candidate Resume
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/resumes/upload`
- **Headers:** 
  - `Authorization: Bearer <candidate_token>`
  - *(Do not manually set Content-Type header in Postman; let it set multipart/form-data with boundary automatically)*
- **Body:** Select **`form-data`**:
  - Key: `file` (Change type dropdown from *Text* to *File*)
  - Value: Select any sample resume `.pdf` or `.docx` on your computer.
- **Expected Response (`201 Created`):**
```json
{
  "id": 1,
  "filename": "alex_johnson_cv.pdf",
  "candidate_name": "Alex Johnson",
  "parsed_skills": [
    "Docker",
    "FastAPI",
    "Git",
    "Linux",
    "PostgreSQL",
    "Python",
    "Redis"
  ],
  "experience_years": 4.5,
  "education_level": "Bachelor",
  "uploaded_at": "2026-09-12T11:47:00.000000",
  "message": "Resume successfully processed and indexed."
}
```

---

### Request 8: Batch Upload Resumes (Recruiter Bulk Upload)
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/resumes/upload-batch`
- **Headers:** 
  - `Authorization: Bearer <recruiter_token>`
- **Body:** Select **`form-data`**:
  - Key: `files` (Type: *File*, select multiple PDF/Word files simultaneously).
- **Expected Response (`201 Created`):** Array of all successfully parsed resumes.

---

### Request 9: Run AI Candidate Screening & Matching
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/matching/job/1/evaluate`
- **Headers:**
  - `Content-Type: application/json`
  - `Authorization: Bearer <recruiter_token>`
- **Body (raw JSON):**
```json
{
  "job_id": 1,
  "resume_ids": null
}
```
*(Passing `"resume_ids": null` automatically screens all candidate resumes stored in the system).*

- **Expected Response (`200 OK`):**
```json
{
  "job_id": 1,
  "job_title": "Senior Python Backend Developer",
  "total_candidates_evaluated": 3,
  "evaluated_at": "2026-09-12T11:48:00.000000",
  "rankings": [
    {
      "resume_id": 1,
      "candidate_name": "Alex Johnson",
      "match_score": 94.7,
      "rank": 1,
      "matched_skills": [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "Redis"
      ],
      "missing_skills": [
        "REST API"
      ],
      "experience_years": 4.5,
      "experience_fit": "Exceeds Requirement (+0.5 yrs)"
    },
    {
      "resume_id": 2,
      "candidate_name": "Candidate: Jane Doe",
      "match_score": 68.2,
      "rank": 2,
      "matched_skills": [
        "Python",
        "PostgreSQL"
      ],
      "missing_skills": [
        "FastAPI",
        "Docker",
        "Redis",
        "REST API"
      ],
      "experience_years": 2.5,
      "experience_fit": "Under Requirement (-1.5 yrs)"
    }
  ]
}
```

---

### Request 10: View Saved Job Rankings (Leaderboard)
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/matching/job/1/rankings`
- **Headers:**
  - `Authorization: Bearer <recruiter_token>`
- **Expected Response (`200 OK`):** Retrieves the persisted ranked candidates table without re-running inference.

---

## 5. Automated Tests Execution

To run the automated test suite locally:

```powershell
$env:PYTHONPATH="backend"
pytest backend/tests -v
```

Expected output:
```text
backend/tests/test_auth.py::test_password_hashing_and_verification PASSED
backend/tests/test_auth.py::test_jwt_token_generation_and_decoding PASSED
backend/tests/test_auth.py::test_job_service_create_and_fetch PASSED
backend/tests/test_ml_matching.py::test_skill_extraction_and_normalization PASSED
backend/tests/test_ml_matching.py::test_experience_extraction_regex PASSED
backend/tests/test_ml_matching.py::test_education_detection PASSED
backend/tests/test_ml_matching.py::test_feature_engineering_pipeline PASSED
backend/tests/test_ml_matching.py::test_predictor_scoring_bounds PASSED
============================== 8 passed in 1.85s ==============================
```
