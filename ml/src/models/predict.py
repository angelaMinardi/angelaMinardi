"""
Fall risk prediction module.

Loads the trained XGBoost model once and provides a predict_risk()
function that returns a risk score, category, and top contributing factors.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import shap
import xgboost as xgb

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "fall_risk_model.json"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.json"


class FallRiskPredictor:
    """Singleton-style predictor with model caching.

    The model and SHAP explainer are loaded once on first use and
    reused for all subsequent predictions.
    """

    _instance: Optional["FallRiskPredictor"] = None

    def __init__(self):
        self._model: Optional[xgb.XGBClassifier] = None
        self._explainer: Optional[shap.TreeExplainer] = None
        self._feature_names: Optional[List[str]] = None

    @classmethod
    def get_instance(cls) -> "FallRiskPredictor":
        """Return the cached singleton predictor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_loaded(self):
        """Lazy-load model, feature names, and SHAP explainer."""
        if self._model is not None:
            return

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Run `python -m ml.src.models.train` first."
            )

        self._model = xgb.XGBClassifier()
        self._model.load_model(str(MODEL_PATH))

        with open(FEATURE_NAMES_PATH) as f:
            self._feature_names = json.load(f)

        self._explainer = shap.TreeExplainer(self._model)

    @property
    def feature_names(self) -> List[str]:
        self._ensure_loaded()
        return self._feature_names

    def predict_risk(self, features: Dict[str, float]) -> Dict:
        """Predict fall risk from extracted gait features.

        Parameters
        ----------
        features : dict
            Feature name -> value mapping.  Must contain all features
            the model was trained on.

        Returns
        -------
        dict with keys:
            score    : float   – probability of high fall risk (0-1)
            category : str     – "low" | "moderate" | "high"
            top_factors : list – top 3 contributing feature names
                                 with direction (e.g. "high sway_rms")
        """
        self._ensure_loaded()

        # Build feature vector in the correct column order
        x = np.array([[features.get(fn, 0.0) for fn in self._feature_names]])

        # Probability of class 1 (high risk)
        score = float(self._model.predict_proba(x)[0, 1])

        # Risk category
        if score < 0.3:
            category = "low"
        elif score <= 0.7:
            category = "moderate"
        else:
            category = "high"

        # SHAP-based top factors
        shap_values = self._explainer.shap_values(x)[0]
        abs_shap = np.abs(shap_values)
        top_indices = np.argsort(abs_shap)[::-1][:3]

        top_factors = []
        for idx in top_indices:
            fname = self._feature_names[idx]
            direction = "high" if shap_values[idx] > 0 else "low"
            top_factors.append(f"{direction} {fname}")

        return {
            "score": round(score, 4),
            "category": category,
            "top_factors": top_factors,
        }

    def predict_risk_batch(self, features_list: List[Dict[str, float]]) -> List[Dict]:
        """Predict risk for multiple feature sets."""
        return [self.predict_risk(f) for f in features_list]


# ── Module-level convenience function ─────────────────────────────────

def predict_risk(features: Dict[str, float]) -> Dict:
    """Convenience wrapper using the singleton predictor."""
    return FallRiskPredictor.get_instance().predict_risk(features)
