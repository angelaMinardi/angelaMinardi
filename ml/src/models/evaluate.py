"""
Evaluate the trained fall-risk XGBoost model.

Generates classification report, ROC curve, SHAP summary,
confusion matrix, and feature importance plots.

Usage:
    python -m ml.src.models.evaluate
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import shap
import xgboost as xgb
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT.parent))

from ml.src.data.loader import load_synthetic_features, split_data, get_feature_columns

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "fall_risk_model.json"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.json"


def load_model_and_data():
    """Load saved model and prepare test data."""
    # Load model
    model = xgb.XGBClassifier()
    model.load_model(str(MODEL_PATH))

    # Load feature names
    with open(FEATURE_NAMES_PATH) as f:
        feature_names = json.load(f)

    # Load and split data (same split as training)
    df = load_synthetic_features()
    X_train, X_test, y_train, y_test = split_data(df, test_size=0.20, random_state=42)

    return model, X_train, X_test, y_train, y_test, feature_names


def print_classification_report(model, X_test, y_test):
    """Print precision, recall, F1 and ROC-AUC."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)
    print(classification_report(y_test, y_pred,
                                target_names=["Low Risk", "High Risk"]))

    auc = roc_auc_score(y_test, y_prob)
    print(f"ROC-AUC Score: {auc:.4f}")
    print("=" * 60)
    return y_pred, y_prob


def plot_roc_curve(y_test, y_prob, save_path=None):
    """Plot and save ROC curve."""
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, color="#2196F3", lw=2,
            label=f"XGBoost (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--",
            label="Random classifier")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curve - Fall Risk Prediction", fontsize=14)
    ax.legend(loc="lower right", fontsize=11)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    save_path = save_path or MODELS_DIR / "roc_curve.png"
    fig.savefig(str(save_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"ROC curve saved to {save_path}")


def plot_confusion_matrix(y_test, y_pred, save_path=None):
    """Plot and save confusion matrix."""
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Low Risk", "High Risk"],
                yticklabels=["Low Risk", "High Risk"],
                ax=ax, annot_kws={"size": 16})
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title("Confusion Matrix - Fall Risk Prediction", fontsize=14)
    plt.tight_layout()

    save_path = save_path or MODELS_DIR / "confusion_matrix.png"
    fig.savefig(str(save_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Confusion matrix saved to {save_path}")


def plot_shap_summary(model, X_test, feature_names, save_path=None):
    """Generate and save SHAP summary plot."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, feature_names=feature_names,
                      show=False, max_display=20)
    plt.title("SHAP Feature Importance - Fall Risk Model", fontsize=14)
    plt.tight_layout()

    save_path = save_path or MODELS_DIR / "shap_summary.png"
    plt.savefig(str(save_path), dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"SHAP summary saved to {save_path}")


def plot_feature_importance(model, feature_names, save_path=None):
    """Plot XGBoost built-in feature importance (gain)."""
    importance = model.feature_importances_
    sorted_idx = np.argsort(importance)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(sorted_idx)), importance[sorted_idx],
            color="#4CAF50", edgecolor="white")
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels([feature_names[i] for i in sorted_idx], fontsize=10)
    ax.set_xlabel("Feature Importance (Gain)", fontsize=12)
    ax.set_title("XGBoost Feature Importance - Fall Risk Model", fontsize=14)
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()

    save_path = save_path or MODELS_DIR / "feature_importance.png"
    fig.savefig(str(save_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Feature importance plot saved to {save_path}")


def evaluate():
    """Run the full evaluation pipeline."""
    print("Loading model and test data...")
    model, X_train, X_test, y_train, y_test, feature_names = load_model_and_data()

    # Classification report
    y_pred, y_prob = print_classification_report(model, X_test, y_test)

    # Plots
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    plot_roc_curve(y_test, y_prob)
    plot_confusion_matrix(y_test, y_pred)
    plot_shap_summary(model, X_test, feature_names)
    plot_feature_importance(model, feature_names)

    print("\nAll evaluation artifacts generated successfully.")


if __name__ == "__main__":
    evaluate()
