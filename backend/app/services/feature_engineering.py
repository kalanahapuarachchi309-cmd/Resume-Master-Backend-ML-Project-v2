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
    