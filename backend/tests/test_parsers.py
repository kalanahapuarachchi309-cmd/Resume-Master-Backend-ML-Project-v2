"""NLP & Parser Unit Test Suite (Hiruna)."""
import pytest
from app.services.nlp.cleaner import TextCleaner
from app.services.nlp.skill_extractor import SkillExtractor

def test_text_cleaning():
    """Verify that URLs and emails are stripped while technical words are preserved."""
    raw = "Reach me at test@example.com or visit https://myblog.com. Proficient in Python and C++."
    cleaned = TextCleaner.clean(raw)
    assert "test@example.com" not in cleaned
    assert "https" not in cleaned
    assert "python" in cleaned
    assert "c++" in cleaned

def test_skill_extraction_taxonomy():
    """Verify that skills from 250+ taxonomy are correctly extracted."""
    sample_text = "Senior Software Engineer with 5 years experience in Python, FastAPI, Docker, and PostgreSQL."
    skills = SkillExtractor.extract_skills(sample_text)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills
    assert "PostgreSQL" in skills

def test_experience_and_education_extraction():
    """Verify experience years and degree tier detection."""
    sample = "Holds a Bachelor of Science in Computer Science with over 4 years of professional experience."
    exp = SkillExtractor.extract_experience_years(sample)
    assert exp >= 4.0
    edu = SkillExtractor.extract_education(sample)
    assert edu == "Bachelor"
