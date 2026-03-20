"""
Train an XGBoost fall-risk classifier on the synthetic gait dataset.

Usage:
    python -m ml.src.models.train
"""

import json
import sys
from pathlib import Path

import numpy as np
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, cross_val_score

# Resolve project paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT.parent))

from ml.src.data.loader import load_synthetic_features, split_data, get_feature_columns

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "fall_risk_model.json"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.json"


def train_model():
    """Train XGBoost classifier with cross-validation and save artifacts."""
    # ── Load data ──────────────────────────────────────────────────
    print("Loading synthetic feature dataset...")
    df = load_synthetic_features()
    X_train, X_test, y_train, y_test = split_data(df, test_size=0.20, random_state=42)
    feature_cols = get_feature_columns(df)

    print(f"Training samples : {len(X_train)}")
    print(f"Test samples     : {len(X_test)}")
    print(f"Features         : {len(feature_cols)}")
    print(f"Class balance    : {np.bincount(y_train)} (train)")
    print(f"                   {np.bincount(y_test)} (test)")

    # ── Class imbalance weight ─────────────────────────────────────
    n_neg = np.sum(y_train == 0)
    n_pos = np.sum(y_train == 1)
    scale_pos_weight = n_neg / max(n_pos, 1)
    print(f"scale_pos_weight : {scale_pos_weight:.2f}")

    # ── XGBoost parameters ─────────────────────────────────────────
    params = {
        "objective": "binary:logistic",
        "max_depth": 5,
        "learning_rate": 0.1,
        "n_estimators": 200,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "eval_metric": "auc",
        "scale_pos_weight": scale_pos_weight,
        "random_state": 42,
        "use_label_encoder": False,
    }

    # ── 5-fold stratified cross-validation ─────────────────────────
    print("\nRunning 5-fold stratified cross-validation...")
    cv_model = xgb.XGBClassifier(**params)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    cv_auc = cross_val_score(cv_model, X_train, y_train,
                             cv=skf, scoring="roc_auc")
    cv_acc = cross_val_score(cv_model, X_train, y_train,
                             cv=skf, scoring="accuracy")
    cv_f1 = cross_val_score(cv_model, X_train, y_train,
                            cv=skf, scoring="f1")

    print(f"  CV ROC-AUC  : {cv_auc.mean():.4f} +/- {cv_auc.std():.4f}")
    print(f"  CV Accuracy : {cv_acc.mean():.4f} +/- {cv_acc.std():.4f}")
    print(f"  CV F1       : {cv_f1.mean():.4f} +/- {cv_f1.std():.4f}")

    # ── Train final model with early stopping ──────────────────────
    print("\nTraining final model with early stopping...")
    model = xgb.XGBClassifier(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    best_iteration = model.best_iteration if hasattr(model, "best_iteration") else params["n_estimators"]
    print(f"  Best iteration: {best_iteration}")

    # ── Evaluate on test set ───────────────────────────────────────
    from sklearn.metrics import roc_auc_score, accuracy_score, f1_score

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    test_auc = roc_auc_score(y_test, y_prob)
    test_acc = accuracy_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred)

    print(f"\n  Test ROC-AUC  : {test_auc:.4f}")
    print(f"  Test Accuracy : {test_acc:.4f}")
    print(f"  Test F1       : {test_f1:.4f}")

    # ── Save model and feature names ───────────────────────────────
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))
    print(f"\nModel saved to {MODEL_PATH}")

    with open(FEATURE_NAMES_PATH, "w") as f:
        json.dump(feature_cols, f, indent=2)
    print(f"Feature names saved to {FEATURE_NAMES_PATH}")

    return model, feature_cols


if __name__ == "__main__":
    train_model()
