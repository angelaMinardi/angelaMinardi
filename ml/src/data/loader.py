"""
Data loading utilities for the Smart Insole ML pipeline.

Provides convenience functions to load the synthetic feature CSV,
raw session pickle, and create train/test splits.
"""

import pickle
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
CSV_PATH = DATA_DIR / "synthetic_gait_data.csv"
PKL_PATH = DATA_DIR / "synthetic_raw_sessions.pkl"


def load_synthetic_features(path: Path = CSV_PATH) -> pd.DataFrame:
    """Load the pre-extracted feature CSV.

    Returns
    -------
    pd.DataFrame with feature columns and a 'label' column.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Feature CSV not found at {path}. "
            "Run `python -m ml.src.data.synthetic` first to generate data."
        )
    df = pd.read_csv(path)
    return df


def load_raw_sessions(path: Path = PKL_PATH) -> list:
    """Load raw session data from the pickle file.

    Returns
    -------
    list of dicts, each containing 'fsr', 'imu', 'fs', 'label', etc.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Raw sessions pickle not found at {path}. "
            "Run `python -m ml.src.data.synthetic` first to generate data."
        )
    with open(path, "rb") as f:
        sessions = pickle.load(f)
    return sessions


def get_feature_columns(df: pd.DataFrame) -> list:
    """Return the list of feature column names (excluding label and session_id)."""
    exclude = {"label", "session_id"}
    return [c for c in df.columns if c not in exclude]


def split_data(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    """Split the feature DataFrame into train/test with stratification on label.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'label' column.
    test_size : float
        Fraction for the test set.
    random_state : int
        Random seed for reproducibility.

    Returns
    -------
    X_train, X_test : pd.DataFrame (feature columns only)
    y_train, y_test : np.ndarray
    """
    feature_cols = get_feature_columns(df)
    X = df[feature_cols]
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        stratify=y,
        random_state=random_state,
    )
    return X_train, X_test, y_train, y_test
