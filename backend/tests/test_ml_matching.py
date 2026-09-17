"""Automated Tests for ML Pipeline, Feature Engineering, and Ranking Engine."""
import pytest
import numpy as np
from app.services.nlp.skill_extractor import SkillExtractor
from app.services.nlp.cleaner import TextCleaner
from app.services.feature_engineering import FeatureEngineeringPipeline
from app.ml.predictor import ResumeMatchPredictor


def test_skill_extraction_and_normalization():
    """Verify that skill aliases are correctly normalized to canonical names."""
    sample_text = "Experienced with JS, ReactJS, Python, Postgres, Docker and K8s. Built RESTful APIs."
    skills = SkillExtractor.extract_skills(sample_text)

    assert "JavaScript" in skills
    assert "React" in skills
    assert "Python" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills


def test_experience_extraction_regex():
    """Verify regex pattern matching for experience phrases."""
    text_1 = "Senior Engineer with 5+ years of professional experience in backend systems."
    assert SkillExtractor.extract_experience_years(text_1) == 5.0

    text_2 = "Full stack developer (2019 - 2023) building enterprise cloud platforms."
    assert SkillExtractor.extract_experience_years(text_2) == 4.0


def test_education_detection():
    """Verify detection of educational qualifications."""
    assert SkillExtractor.extract_education("Graduated with BSc in Computer Science") == "Bachelor"
    assert SkillExtractor.extract_education("Completed MSc in Data Analytics") == "MSc"
    assert SkillExtractor.extract_education("Ph.D in Artificial Intelligence") == "PhD"
    assert SkillExtractor.extract_education("Self-taught developer") == "None"


def test_feature_engineering_pipeline():
    """Verify that the 7-feature numerical vector and explainability payload are generated."""
    resume_text = "Python FastAPI Docker PostgreSQL developer with 4 years experience."
    job_desc = "Seeking Python FastAPI developer with Docker and PostgreSQL. 3+ years exp required."
    candidate_skills = ["Python", "FastAPI", "Docker", "PostgreSQL"]
    required_skills = ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"]

    features, explain = FeatureEngineeringPipeline.extract_features(
        resume_text=resume_text,
        job_description=job_desc,
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        candidate_exp=4.0,
        required_exp=3.0,
        candidate_edu="Bachelor",
    )

    # Validate shape (1 row, 7 feature columns)
    assert features.shape == (1, 7)

    # Validate explainability contents
    assert len(explain["matched_skills"]) == 4
    assert explain["missing_skills"] == ["AWS"]
    assert explain["experience_fit"] == "Exceeds Requirement (+1.0 yrs)"
    assert explain["skill_match_percentage"] == 80.0


def test_predictor_scoring_bounds():
    """Verify that predictor always produces a valid score between 0.0% and 100.0%."""
    predictor = ResumeMatchPredictor()
    dummy_features = np.array([[0.8, 0.9, 4.0, 0.2, 1.0, 1.0, 2.0]], dtype=np.float32)

    score = predictor.predict_match_probability(dummy_features)
    assert 0.0 <= score <= 100.0


