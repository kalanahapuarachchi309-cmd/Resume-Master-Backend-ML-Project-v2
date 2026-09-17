# Resume Master: AI-Powered Candidate Screening & Job Matching Platform

An end-to-end Machine Learning recruitment platform integrating **FastAPI**, **PostgreSQL / SQLite**, **Scikit-Learn**, and **React 18** to automatically ingest, parse, evaluate, rank, and explain candidate resumes against job requisitions.

---

## 🏛️ System Architecture

The application implements a decoupled, production-ready architecture conforming to industry-standard ML engineering practices:

```
                      ┌────────────────────────────────────────────────────────┐
                      │              REACT 18 SINGLE PAGE APP (SPA)            │
                      │  - Recruiter Job Posting & Candidate Portal (Tailwind) │
                      │  - Drag-and-Drop Resume Ingestion & Parsing Preview    │
                      │  - Ranked Candidate Leaderboard & XAI Skill Gap UI     │
                      └───────────────────────────┬────────────────────────────┘
                                                  │ HTTP REST (JSON / Multipart)
                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FASTAPI REST BACKEND SERVICES                                          │
├────────────────────────────────────────┬───────────────────────────────────────────────────────────────┤
│          AUTHENTICATION & RBAC         │                   JOB REQUISITION SERVICE                     │
│  - JWT Bearer Authentication (HS256)   │  - Job Creation, Update, Deletion & Search                    │
│  - Bcrypt Cryptographic Password Hash  │  - Recruiter Ownership Authorization                          │
│  - Role Guard (Admin/Recruiter/User)   │  - Cloudinary Raw Document Storage & CDN Retrieval            │
└───────────────────┬────────────────────┴───────────────────────────────┬───────────────────────────────┘
                    │                                                   │
     Database ORM   │                                 Unstructured Docs │ (PDF / DOCX)
     Persistence    ▼                                                   ▼
┌───────────────────────────┐                    ┌──────────────────────────────────────────────────────┐
│       SQL DATABASE        │                    │         DOCUMENT INGESTION & NLP PREPROCESSING       │
│  - Users & Credentials    │                    │  - Multi-Column PDF Spatial Parsing (`pdfplumber`)   │
│  - Job Requisitions       │                    │  - Word Document Parsing (`python-docx`)             │
│  - Resumes & Metadata     │                    │  - Kerning Repair & Character Normalization          │
│  - Candidate Match Scores │                    │  - 250+ Technical Skill Taxonomy & Regex Extraction  │
└───────────────────────────┘                    └──────────────────────────┬───────────────────────────┘
                                                                            │ Extracted Features
                                                                            ▼
                                                 ┌──────────────────────────────────────────────────────┐
                                                 │        MACHINE LEARNING MATCHING & RANKING ENGINE    │
                                                 │  - 6-Stage Mandatory Feature Engineering Pipeline    │
                                                 │  - TF-IDF Vectorization (Unigrams + Bigrams)         │
                                                 │  - Jaccard Skill Overlap Ratio                       │
                                                 │  - Random Forest Classifier (`model.pkl`)            │
                                                 │  - Calibrated Match Scoring & Explainable AI (XAI)   │
                                                 └──────────────────────────────────────────────────────┘
```

---

## ⚙️ Mandatory 6-Stage Feature Engineering Pipeline

Implemented in `backend/app/services/feature_engineering.py`:

1. **Text Feature Extraction**: TF-IDF (Term Frequency-Inverse Document Frequency) vectorization computed across candidate resume text and target job requisitions using combined unigrams and bigrams.
2. **Feature Interaction & Overlap Ratio**: Jaccard similarity index measuring skill set intersection over job requirements:
   $$\text{Skill Overlap Ratio} = \frac{|\text{Resume Skills} \cap \text{Job Skills}|}{|\text{Job Skills}|}$$
3. **Domain Metric Engineering**: Experience delta calculation capturing career seniority alignment:
   $$\text{Experience Delta} = \text{Candidate Years of Experience} - \text{Required Years of Experience}$$
4. **Categorical Encoding**: Ordinal mapping of educational qualifications into standardized numeric levels:
   $$\text{None} \to 0,\; \text{Diploma} \to 1,\; \text{Bachelor} \to 2,\; \text{Master} \to 3,\; \text{PhD} \to 4$$
5. **Missing Value Imputation**: Median and domain-mode fallback imputation for unmentioned candidate experience and education fields.
6. **Feature Scaling & Normalization**: Min-Max scaling across synthesized composite match vectors to generate calibrated $[0.0, 1.0]$ prediction inputs.

---

## 📂 Project Repository Structure

```text
Resume-Master-v2/
├── backend/
│   ├── app/
│   │   ├── main.py                         # FastAPI application entrypoint, CORS, route registration
│   │   │
│   │   ├── core/                           # Application Security & Configuration
│   │   │   ├── config.py                   # Pydantic Settings (.env configuration loader)
│   │   │   └── security.py                 # JWT token generation, Bcrypt password hashing, RBAC
│   │   │
│   │   ├── database/                       # Database Engine & Initialization
│   │   │   ├── base.py                     # SQLAlchemy declarative model registry
│   │   │   ├── connection.py               # Engine, sessionmaker, and get_db dependency
│   │   │   └── seed.py                     # Default user seeder (Admin, Recruiter, Candidate)
│   │   │
│   │   ├── models/                         # SQLAlchemy ORM Models
│   │   │   ├── user.py                     # User model with RBAC role enumeration
│   │   │   ├── job.py                      # Job requisition model
│   │   │   ├── resume.py                   # Resume metadata, raw text, and parsed skills
│   │   │   └── match_result.py             # Match evaluation scores and rankings
│   │   │
│   │   ├── schemas/                        # Pydantic Request & Response DTOs
│   │   │   ├── auth.py                     # Login, registration, and token schemas
│   │   │   ├── job.py                      # Job request/response schemas
│   │   │   ├── resume.py                   # Resume upload & parsed attribute schemas
│   │   │   └── matching.py                 # Candidate match ranking & explainability schemas
│   │   │
│   │   ├── routes/                         # REST API Route Controllers
│   │   │   ├── auth.py                     # POST /api/auth/register, POST /api/auth/login, /me
│   │   │   ├── users.py                    # User profile and administrative management
│   │   │   ├── jobs.py                     # POST, GET, PUT, DELETE /api/jobs
│   │   │   ├── resumes.py                  # POST /api/resumes/upload (single & bulk)
│   │   │   └── matching.py                 # POST /api/matching/job/{id}/evaluate
│   │   │
│   │   ├── services/                       # Business Logic Layer
│   │   │   ├── job_service.py              # Job search, filtering, ownership validation
│   │   │   ├── cloudinary_service.py       # Cloudinary raw file upload & CDN link persistence
│   │   │   ├── parsers/                    # Multi-format Document Parsers
│   │   │   │   ├── pdf_parser.py           # Multi-column PDF extractor via pdfplumber
│   │   │   │   └── docx_parser.py          # Word document extractor via python-docx
│   │   │   ├── nlp/                        # Natural Language Processing
│   │   │   │   ├── cleaner.py              # Text cleaning, regex, kerning repair
│   │   │   │   └── skill_extractor.py      # Technical taxonomy & experience extractor
│   │   │   ├── feature_engineering.py      # 6 Feature engineering transformations
│   │   │   └── ranking_service.py          # Candidate scoring, ranking, explainability
│   │   │
│   │   └── ml/                             # Machine Learning Artifacts & Predictor
│   │       ├── predictor.py                # Model loader and inference execution wrapper
│   │       ├── model.pkl                   # Trained Random Forest Classifier
│   │       └── vectorizer.pkl              # Fitted TF-IDF Vectorizer
│   │
│   ├── tests/                              # Automated Unit Test Suite
│   │   ├── test_auth.py                    # Auth & security tests
│   │   └── test_ml_matching.py             # Feature engineering & ML inference tests
│   ├── requirements.txt                    # Backend Python dependencies
│   ├── .env.example                        # Template environment variables
│   ├── Procfile                            # Cloud deployment entrypoint
│   └── render.yaml                         # 1-Click Render blueprint configuration
│
├── ml_pipeline/                            # Offline Machine Learning Training Pipeline
│   ├── train_and_evaluate.py               # Dataset generation, model training & benchmark script
│   └── EVALUATION_REPORT.md                # Accuracy, Precision, Recall & F1-Score report
│
├── frontend/                               # React 18 SPA (Separate Git Repository)
│   ├── src/
│   │   ├── components/                     # Navbar, ProtectedRoute
│   │   ├── context/                        # AuthContext (JWT & user state)
│   │   ├── pages/                          # Login, Register, Dashboard, JobsList, ResumeUpload, MatchingDashboard
│   │   ├── services/                       # Axios api client with Bearer interceptor
│   │   ├── App.jsx                         # React routing
│   │   └── main.jsx                        # React root mount
│   ├── package.json                        # Node dependencies
│   └── vite.config.js                      # Vite bundler config
│
├── uploads/                                # Sample resume files (PDF, DOCX) for testing
├── run_backend.bat                         # 1-Click Windows batch backend launcher
├── run_backend.ps1                         # 1-Click PowerShell backend launcher
├── seed_users.py                           # Standalone database user seeder
├── TESTING_GUIDE.md                        # Complete API testing & Postman guide
└── README.md                               # Project documentation
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm 9+
- Git

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed default database accounts (Admin, Recruiter, Candidate)
python app/database/seed.py

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive Swagger API documentation will be available at: **`http://localhost:8000/docs`**

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
The React frontend will be running at: **`http://localhost:5173`**

### 4. Default Seeded Credentials
| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@resumemaster.com` | `Admin123!` |
| **Recruiter** | `recruiter@techcorp.com` | `Recruiter123!` |
| **Candidate** | `candidate@example.com` | `Candidate123!` |

---

## 🧪 Automated Testing
Run the backend test suite covering authentication, password hashing, job creation, NLP entity extraction, feature engineering, and candidate ranking:
```bash
pytest backend/tests -v
```
