"""Mandatory Feature Engineering Pipeline (Assignment Section 5 - Mahen & Team).

Implements the unified 7 feature engineering techniques used identically during training & runtime:
1. TF-IDF Text Semantic Similarity (via pre-fitted vectorizer - no runtime refitting)
2. Skill Overlap Ratio (Jaccard intersection)
3. Matched Skill Count
4. Missing Skill Ratio
5. Domain Metric: Experience Delta
6. Experience Fit Binary Indicator
7. Categorical Encoding: Education Degree Ordinal Tier
8. Missing Value Imputation
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from app.services.nlp.cleaner import TextCleaner

def normalize_degree(degree_str: Optional[str]) -> Tuple[str, int]:
    """Returns (canonical_display_name, ordinal_tier 0-4)."""
    if not degree_str:
        return "None", 0
    d = str(degree_str).lower().strip()
    if any(k in d for k in ["phd", "doctor"]):
        return "PhD", 4
    if any(k in d for k in ["master", "msc", "mba", "m.tech", "postgraduate"]):
        return "Master's Degree", 3
    if any(k in d for k in ["bachelor", "bsc", "b.tech", "undergraduate", "b.e", "bba", "degree"]):
        return "Bachelor's Degree", 2
    if any(k in d for k in ["diploma", "associate", "higher diploma"]):
        return "Associate / Diploma", 1
    if any(k in d for k in ["high school", "secondary"]):
        return "High School", 0
    return "Not Specified", 0


class FeatureEngineeringPipeline:
    """Production feature engineering pipeline matching the offline training pipeline."""

    _vectorizer = None

    @classmethod
    def get_vectorizer(cls):
        """Lazy load the pre-trained TF-IDF vectorizer artifact."""
        if cls._vectorizer is None:
            vec_path = os.path.join(os.path.dirname(__file__), "..", "ml", "vectorizer.pkl")
            if os.path.exists(vec_path):
                try:
                    with open(vec_path, "rb") as f:
                        cls._vectorizer = pickle.load(f)
                except Exception:
                    cls._vectorizer = None
        return cls._vectorizer

    @classmethod
    def extract_features(
        cls,
        resume_text: str,
        job_description: str,
        candidate_skills: List[str],
        required_skills: List[str],
        candidate_exp: Optional[float] = None,
        required_exp: Optional[float] = 0.0,
        candidate_edu: Optional[str] = "None",
        required_edu: Optional[str] = "Bachelor",
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Transforms a candidate resume & job description into a model-ready 1x7 feature vector
        and returns explainable insights.
        """
        # --- Technique 8: Missing Value Imputation ---
        clean_cand_exp = 0.0 if (candidate_exp is None or np.isnan(candidate_exp)) else float(candidate_exp)
        clean_req_exp = 0.0 if (required_exp is None or np.isnan(required_exp)) else float(required_exp)
        
        cand_edu_name, cand_edu_tier = normalize_degree(candidate_edu)
        req_edu_name, req_edu_tier = normalize_degree(required_edu)

        # --- Technique 1: TF-IDF Text Similarity with pre-fitted vectorizer ---
        vectorizer = cls.get_vectorizer()
        if vectorizer is not None and resume_text and job_description:
            try:
                c_resume = TextCleaner.remove_stopwords(resume_text)
                c_job = TextCleaner.remove_stopwords(job_description)
                vec_r = vectorizer.transform([c_resume])
                vec_j = vectorizer.transform([c_job])
                tfidf_sim = float(cosine_similarity(vec_r, vec_j)[0][0])
            except Exception:
                tfidf_sim = 0.0
        else:
            tfidf_sim = 0.0

        # --- Technique 2, 3, 4: Skill Features & Overlap ---
        c_set = set(s.lower().strip() for s in (candidate_skills or []))
        r_set = set(s.lower().strip() for s in (required_skills or []))

        matched_skills = [s for s in (required_skills or []) if s.lower().strip() in c_set]
        missing_skills = [s for s in (required_skills or []) if s.lower().strip() not in c_set]

        if r_set:
            skill_overlap_ratio = len(matched_skills) / len(r_set)
            missing_skill_ratio = len(missing_skills) / len(r_set)
        else:
            skill_overlap_ratio = 1.0
            missing_skill_ratio = 0.0

        skill_count = float(len(matched_skills))

        # --- Technique 5: Domain Metric: Experience Delta ---
        exp_delta = float(np.clip(clean_cand_exp - clean_req_exp, -3.0, 3.0))

        # --- Technique 6: Experience Fit Binary ---
        exp_fit_binary = 1.0 if clean_cand_exp >= clean_req_exp else 0.0

        # --- Technique 7: Education Degree Ordinal Encoding ---
        edu_ordinal = float(cand_edu_tier)

        # 1x7 Feature vector identical to model training matrix:
        feature_vector = np.array([[
            tfidf_sim,
            skill_overlap_ratio,
            skill_count,
            missing_skill_ratio,
            exp_delta,
            exp_fit_binary,
            edu_ordinal,
        ]], dtype=np.float32)

        # Human-readable experience explainability description
        if clean_cand_exp >= clean_req_exp + 1.0:
            exp_summary = f"Exceeds Requirement (+{round(clean_cand_exp - clean_req_exp, 1)} yrs)"
        elif clean_cand_exp >= clean_req_exp:
            exp_summary = "Meets Requirement"
        else:
            gap = round(clean_req_exp - clean_cand_exp, 1)
            exp_summary = f"Under Requirement (-{gap} yrs)"

        # Education fit assessment
        if cand_edu_tier > req_edu_tier:
            edu_fit_summary = f"Exceeds Requirement ({cand_edu_name})"
        elif cand_edu_tier == req_edu_tier and cand_edu_tier > 0:
            edu_fit_summary = f"Meets Requirement ({cand_edu_name})"
        elif cand_edu_tier < req_edu_tier and cand_edu_tier > 0:
            edu_fit_summary = f"Under Requirement ({cand_edu_name} vs {req_edu_name})"
        else:
            edu_fit_summary = f"Requires {req_edu_name}"

        explainability = {
            "tfidf_similarity": round(tfidf_sim * 100.0, 1),
            "skill_match_percentage": round(skill_overlap_ratio * 100.0, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_fit": exp_summary,
            "experience_years": clean_cand_exp,
            "education_level": cand_edu_name,
            "education_fit": edu_fit_summary,
        }

        return feature_vector, explainability
