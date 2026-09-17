# FastAPI REST Backend Service

This module houses the RESTful API service, authentication guards, database models, document parsing pipelines, and machine learning inference services for the Resume Master platform.

---

## 📂 Backend Architecture

```text
backend/
├── app/
│   ├── core/                           # Security, JWT tokens, and Pydantic configuration
│   ├── database/                       # Database engine, session management, and seed scripts
│   ├── models/                         # SQLAlchemy ORM models (User, Job, Resume, MatchResult)
│   ├── schemas/                        # Pydantic DTO validation schemas
│   ├── routes/                         # API route endpoints (Auth, Users, Jobs, Resumes, Matching)
│   ├── services/                       # Business logic layer
│   │   ├── parsers/                    # Multi-column PDF and DOCX document extractors
│   │   └── nlp/                        # NLP text cleaner, skill taxonomy, and regex extractors
│   └── ml/                             # ML model loader and candidate scoring predictor
├── tests/                              # Automated unit tests
├── requirements.txt                    # Python runtime dependencies
├── .env.example                        # Template environment variables
├── Procfile                            # Cloud deployment entrypoint
└── render.yaml                         # 1-Click cloud blueprint
```

---

## 🚀 Running the Backend

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API Documentation: `http://localhost:8000/docs`
