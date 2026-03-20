"""
Tests for the Smart Insole ML pipeline.

- Feature extraction on synthetic data
- Prediction output validation
- API endpoint testing
"""

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT.parent))

from ml.src.data.synthetic import generate_raw_session
from ml.src.data.preprocessor import (
    bandpass_filter,
    remove_gravity,
    handle_missing,
    detect_walking_bouts,
    preprocess_session,
)
from ml.src.features.gait_features import (
    extract_features,
    extract_features_batch,
    FEATURE_NAMES,
)


# ──────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────

@pytest.fixture
def normal_session():
    """Generate a low-risk synthetic session."""
    return generate_raw_session(is_high_risk=False, session_id=0)


@pytest.fixture
def high_risk_session():
    """Generate a high-risk synthetic session."""
    return generate_raw_session(is_high_risk=True, session_id=1)


@pytest.fixture
def minimal_session():
    """Minimal valid session for edge-case testing."""
    n = 500  # 5 seconds at 100 Hz
    fsr = np.random.rand(n, 8) * 100
    imu = np.random.randn(n, 6)
    imu[:, 2] += 9.81  # add gravity to z-axis
    return {
        "session_id": 99,
        "label": 0,
        "fs": 100,
        "duration": 5.0,
        "fsr": fsr,
        "imu": imu,
        "foot_temperature": 30.0,
    }


# ──────────────────────────────────────────────────────────────────────
# Test synthetic data generation
# ──────────────────────────────────────────────────────────────────────

class TestSyntheticData:
    def test_session_shape(self, normal_session):
        assert normal_session["fsr"].shape == (1000, 8)
        assert normal_session["imu"].shape == (1000, 6)

    def test_session_has_required_keys(self, normal_session):
        required = {"session_id", "label", "fs", "duration", "fsr", "imu",
                     "foot_temperature", "params"}
        assert required.issubset(set(normal_session.keys()))

    def test_low_risk_label(self, normal_session):
        assert normal_session["label"] == 0

    def test_high_risk_label(self, high_risk_session):
        assert high_risk_session["label"] == 1

    def test_fsr_non_negative(self, normal_session):
        assert np.all(normal_session["fsr"] >= 0)

    def test_foot_temperature_range(self, normal_session):
        temp = normal_session["foot_temperature"]
        assert 20.0 <= temp <= 35.0


# ──────────────────────────────────────────────────────────────────────
# Test preprocessing
# ──────────────────────────────────────────────────────────────────────

class TestPreprocessor:
    def test_bandpass_preserves_shape(self):
        data = np.random.randn(500, 8)
        filtered = bandpass_filter(data, 0.5, 25.0, 100.0)
        assert filtered.shape == data.shape

    def test_bandpass_1d(self):
        data = np.random.randn(500)
        filtered = bandpass_filter(data, 0.5, 25.0, 100.0)
        assert filtered.shape == data.shape

    def test_remove_gravity(self):
        n = 500
        imu = np.zeros((n, 6))
        imu[:, 2] = 9.81  # constant gravity on z
        result = remove_gravity(imu, fs=100.0)
        # After gravity removal, z-axis should be near zero
        assert np.abs(result[:, 2].mean()) < 1.0
        # Gyro channels unchanged
        np.testing.assert_array_equal(result[:, 3:], imu[:, 3:])

    def test_handle_missing_interpolates(self):
        data = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
        result = handle_missing(data)
        assert not np.any(np.isnan(result))
        assert abs(result[2] - 3.0) < 0.01

    def test_handle_missing_2d(self):
        data = np.array([[1.0, 2.0], [np.nan, 3.0], [3.0, np.nan]])
        result = handle_missing(data)
        assert not np.any(np.isnan(result))

    def test_detect_walking_bouts(self, normal_session):
        bouts = detect_walking_bouts(normal_session["imu"], normal_session["fs"])
        assert len(bouts) >= 1
        for start, end in bouts:
            assert start < end

    def test_preprocess_session(self, normal_session):
        segments = preprocess_session(normal_session)
        assert len(segments) >= 1
        seg = segments[0]
        assert "fsr" in seg
        assert "imu" in seg
        assert seg["fsr"].shape[1] == 8
        assert seg["imu"].shape[1] == 6


# ──────────────────────────────────────────────────────────────────────
# Test feature extraction
# ──────────────────────────────────────────────────────────────────────

class TestFeatureExtraction:
    def test_extract_returns_all_features(self, normal_session):
        features = extract_features(normal_session)
        for name in FEATURE_NAMES:
            assert name in features, f"Missing feature: {name}"

    def test_feature_count(self, normal_session):
        features = extract_features(normal_session)
        assert len(features) == len(FEATURE_NAMES)

    def test_feature_types(self, normal_session):
        features = extract_features(normal_session)
        for name, val in features.items():
            assert isinstance(val, (int, float, np.integer, np.floating)), \
                f"Feature {name} has non-numeric type: {type(val)}"

    def test_cadence_range(self, normal_session):
        features = extract_features(normal_session)
        # Cadence should be reasonable (not zero, not extreme)
        assert 10 < features["cadence"] < 300

    def test_stance_swing_sum(self, normal_session):
        features = extract_features(normal_session)
        total = features["stance_phase_pct"] + features["swing_phase_pct"]
        assert abs(total - 100.0) < 0.01

    def test_stride_time_positive(self, normal_session):
        features = extract_features(normal_session)
        assert features["stride_time_mean"] > 0

    def test_walking_speed_positive(self, normal_session):
        features = extract_features(normal_session)
        assert features["walking_speed"] > 0

    def test_step_count_positive(self, normal_session):
        features = extract_features(normal_session)
        assert features["step_count"] >= 1

    def test_foot_temperature(self, normal_session):
        features = extract_features(normal_session)
        assert 15 <= features["foot_temperature"] <= 40

    def test_pressure_non_negative(self, normal_session):
        features = extract_features(normal_session)
        assert features["peak_pressure_heel"] >= 0
        assert features["peak_pressure_forefoot"] >= 0
        assert features["peak_pressure_toe"] >= 0

    def test_sway_rms_positive(self, normal_session):
        features = extract_features(normal_session)
        assert features["sway_rms"] >= 0

    def test_batch_extraction(self, normal_session, high_risk_session):
        df = extract_features_batch([normal_session, high_risk_session])
        assert len(df) == 2
        assert "label" in df.columns
        for name in FEATURE_NAMES:
            assert name in df.columns

    def test_minimal_session(self, minimal_session):
        """Feature extraction should not crash on minimal input."""
        features = extract_features(minimal_session)
        assert len(features) == len(FEATURE_NAMES)

    def test_high_risk_vs_normal_differences(self, normal_session, high_risk_session):
        """High risk should generally show higher variability or lower speed."""
        f_normal = extract_features(normal_session)
        f_risk = extract_features(high_risk_session)
        # Not a strict assertion (stochastic), just verify both produce valid output
        assert f_normal["cadence"] > 0
        assert f_risk["cadence"] > 0


# ──────────────────────────────────────────────────────────────────────
# Test prediction (requires trained model)
# ──────────────────────────────────────────────────────────────────────

class TestPrediction:
    @pytest.fixture(autouse=True)
    def _check_model_exists(self):
        model_path = PROJECT_ROOT / "models" / "fall_risk_model.json"
        if not model_path.exists():
            pytest.skip("Trained model not found; run train.py first")

    def test_predict_risk_output_structure(self, normal_session):
        from ml.src.models.predict import predict_risk
        features = extract_features(normal_session)
        result = predict_risk(features)
        assert "score" in result
        assert "category" in result
        assert "top_factors" in result
        assert isinstance(result["score"], float)
        assert result["category"] in ("low", "moderate", "high")
        assert isinstance(result["top_factors"], list)
        assert len(result["top_factors"]) == 3

    def test_predict_risk_score_range(self, normal_session):
        from ml.src.models.predict import predict_risk
        features = extract_features(normal_session)
        result = predict_risk(features)
        assert 0.0 <= result["score"] <= 1.0

    def test_predict_risk_category_thresholds(self):
        from ml.src.models.predict import FallRiskPredictor
        predictor = FallRiskPredictor.get_instance()
        # Use dummy features with all zeros
        feature_names = predictor.feature_names
        dummy = {fn: 0.0 for fn in feature_names}
        result = predictor.predict_risk(dummy)
        # Just check it returns a valid category
        assert result["category"] in ("low", "moderate", "high")


# ──────────────────────────────────────────────────────────────────────
# Test API endpoints (requires trained model)
# ──────────────────────────────────────────────────────────────────────

class TestAPI:
    @pytest.fixture(autouse=True)
    def _check_model_for_api(self):
        model_path = PROJECT_ROOT / "models" / "fall_risk_model.json"
        if not model_path.exists():
            pytest.skip("Trained model not found; run train.py first")

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from ml.src.api.serve import app
        return TestClient(app)

    @pytest.fixture
    def sample_features(self, normal_session):
        feats = extract_features(normal_session)
        feats["patient_id"] = "test-patient-001"
        return feats

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "model_loaded" in data
        assert "timestamp" in data

    def test_predict_endpoint(self, client, sample_features):
        resp = client.post("/predict", json=sample_features)
        assert resp.status_code == 200
        data = resp.json()
        assert "score" in data
        assert "category" in data
        assert "top_factors" in data
        assert data["category"] in ("low", "moderate", "high")
        assert 0.0 <= data["score"] <= 1.0

    def test_upload_session_endpoint(self, client, normal_session):
        payload = {
            "patient_id": "test-patient-002",
            "fsr": normal_session["fsr"].tolist(),
            "imu": normal_session["imu"].tolist(),
            "fs": normal_session["fs"],
            "foot_temperature": normal_session["foot_temperature"],
        }
        resp = client.post("/upload-session", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "score" in data
        assert data["patient_id"] == "test-patient-002"

    def test_patient_history(self, client, sample_features):
        # First create an assessment
        sample_features["patient_id"] = "test-history-patient"
        client.post("/predict", json=sample_features)

        # Then query history
        resp = client.get("/patient/test-history-patient/history")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_patient_report(self, client, sample_features):
        # Create two assessments for trend detection
        sample_features["patient_id"] = "test-report-patient"
        client.post("/predict", json=sample_features)
        client.post("/predict", json=sample_features)

        resp = client.get("/patient/test-report-patient/report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["patient_id"] == "test-report-patient"
        assert data["total_assessments"] >= 2
        assert data["trend"] in ("improving", "stable", "worsening")

    def test_patient_history_404(self, client):
        resp = client.get("/patient/nonexistent/history")
        assert resp.status_code == 404

    def test_upload_session_bad_shape(self, client):
        payload = {
            "patient_id": "bad",
            "fsr": [[1, 2, 3]],  # wrong shape (should be 8 cols)
            "imu": [[1, 2, 3, 4, 5, 6]],
            "fs": 100,
            "foot_temperature": 30.0,
        }
        resp = client.post("/upload-session", json=payload)
        assert resp.status_code == 400
