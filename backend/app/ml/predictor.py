"""Machine Learning Model Inference Service (Hiruna, Sampath & Team)."""
import os
import pickle
import logging
from typing import Optional, Any
import numpy as np

logger = logging.getLogger(__name__)


class ResumeMatchPredictor:
    """Loads trained ML classification model and predicts candidate-job suitability percentage."""

    def __init__(self, model_path: Optional[str] = None):
        base_dir = os.path.dirname(__file__)
        self.model_path = model_path or os.path.join(base_dir, "model.pkl")
        self.model: Optional[Any] = None
        self.model_name: str = "Unavailable"
        self.load_model()

    def load_model(self) -> bool:
        """Load pickled scikit-learn model from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                self.model_name = type(self.model).__name__
                logger.info(f"Loaded trained ML model: {self.model_name}")
                return True
            except Exception as e:
                logger.error(f"Error loading ML model from {self.model_path}: {e}")
                self.model = None
                self.model_name = "Error Loading"
                return False
        else:
            logger.warning(f"ML model artifact not found at {self.model_path}.")
            return False

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    def predict_match_probability(self, feature_vector: np.ndarray) -> float:
        """Predict candidate suitability probability using the trained ML model.

        Combines trained ML model probability with calibrated domain feature weighting
        to provide smooth, accurate, explainable candidate ranking (0.0% to 100.0%).
        """
        try:
            tfidf_sim = float(feature_vector[0][0])
            skill_overlap = float(feature_vector[0][1])
            exp_delta = float(feature_vector[0][4])
            exp_fit = float(feature_vector[0][5])
            edu_ordinal = float(feature_vector[0][6])

            # Domain continuous feature evaluation
            exp_score = 1.0 if exp_fit else max(0.2, 1.0 + (exp_delta / 4.0))
            edu_score = min(1.0, max(0.4, edu_ordinal / 2.0))
            feature_score = (skill_overlap * 0.55) + (exp_score * 0.25) + (tfidf_sim * 0.12) + (edu_score * 0.08)
            feature_pct = feature_score * 100.0

            if self.model is not None:
                ml_proba = float(self.model.predict_proba(feature_vector)[0][1]) * 100.0
                # 60% ML Random Forest decision probability, 40% granular domain feature calibration
                final_score = (ml_proba * 0.60) + (feature_pct * 0.40)
                if skill_overlap >= 0.85:
                    final_score = max(final_score, 82.0 + (exp_fit * 12.0))
                elif skill_overlap <= 0.20:
                    final_score = min(final_score, 35.0)
                return round(float(np.clip(final_score, 0.0, 100.0)), 1)

            return round(float(np.clip(feature_pct, 5.0, 99.0)), 1)
        except Exception as e:
            logger.error(f"Prediction calculation error: {e}")
            return 50.0


# Singleton predictor service
predictor_service = ResumeMatchPredictor()
