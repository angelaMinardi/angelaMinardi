"""
FastAPI application for the Smart Insole Fall Risk Prediction system.

Endpoints:
    POST /predict            – predict fall risk from gait features
    POST /upload-session     – upload raw sensor data, extract features, predict
    GET  /patient/{id}/history – historical risk assessments
    GET  /patient/{id}/report  – detailed report data
    GET  /health             – health check

Usage:
    uvicorn ml.src.api.serve:app --reload --port 8000
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT.parent))

from ml.src.features.gait_features import extract_features, FEATURE_NAMES
from ml.src.models.predict import FallRiskPredictor

# ──────────────────────────────────────────────────────────────────────
# Pydantic models
# ──────────────────────────────────────────────────────────────────────

class GaitFeatures(BaseModel):
    """Input schema: pre-extracted gait features."""
    stride_time_mean: float = Field(..., description="Mean stride time (s)")
    stride_time_cv: float = Field(..., description="Stride time CV (%)")
    step_time_mean: float = Field(..., description="Mean step time (s)")
    step_time_cv: float = Field(..., description="Step time CV (%)")
    stance_phase_pct: float = Field(..., description="Stance phase (%)")
    swing_phase_pct: float = Field(..., description="Swing phase (%)")
    double_support_pct: float = Field(..., description="Double support (%)")
    cadence: float = Field(..., description="Steps per minute")
    stride_length_mean: float = Field(..., description="Mean stride length (m)")
    stride_length_cv: float = Field(..., description="Stride length CV (%)")
    walking_speed: float = Field(..., description="Walking speed (m/s)")
    peak_pressure_heel: float = Field(..., description="Peak heel pressure")
    peak_pressure_midfoot: float = Field(..., description="Peak midfoot pressure")
    peak_pressure_forefoot: float = Field(..., description="Peak forefoot pressure")
    peak_pressure_toe: float = Field(..., description="Peak toe pressure")
    cop_displacement_ap: float = Field(..., description="AP COP displacement")
    cop_displacement_ml: float = Field(..., description="ML COP displacement")
    pressure_symmetry_index: float = Field(..., description="Pressure symmetry index")
    heel_to_toe_transfer_time: float = Field(..., description="Heel-to-toe transfer time (s)")
    total_ground_reaction_force: float = Field(..., description="Mean total GRF")
    stride_variability_index: float = Field(..., description="Stride variability index")
    cop_path_length: float = Field(..., description="COP path length")
    sway_rms: float = Field(..., description="Sway RMS (m/s^2)")
    foot_temperature: float = Field(..., description="Foot temperature (C)")
    step_count: int = Field(..., description="Number of steps")
    patient_id: Optional[str] = Field(None, description="Patient identifier")


class RiskAssessment(BaseModel):
    """Output schema: fall risk assessment."""
    assessment_id: str
    timestamp: str
    score: float = Field(..., description="Risk probability 0-1")
    category: str = Field(..., description="low | moderate | high")
    top_factors: List[str] = Field(..., description="Top 3 contributing factors")
    patient_id: Optional[str] = None


class RawSessionUpload(BaseModel):
    """Input schema for raw sensor data upload."""
    patient_id: str
    fsr: List[List[float]] = Field(..., description="FSR data (n_samples x 8)")
    imu: List[List[float]] = Field(..., description="IMU data (n_samples x 6)")
    fs: float = Field(100.0, description="Sampling frequency (Hz)")
    foot_temperature: float = Field(30.0, description="Foot temperature (C)")


class PatientReport(BaseModel):
    """Detailed patient report."""
    patient_id: str
    total_assessments: int
    latest_score: Optional[float]
    latest_category: Optional[str]
    average_score: float
    trend: str  # "improving", "stable", "worsening"
    assessments: List[RiskAssessment]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    timestamp: str


# ──────────────────────────────────────────────────────────────────────
# In-memory storage
# ──────────────────────────────────────────────────────────────────────

# patient_id -> list of RiskAssessment dicts
assessment_store: Dict[str, List[dict]] = {}


# ──────────────────────────────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Smart Insole Fall Risk API",
    description="ML-powered fall risk prediction from insole gait data",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _store_assessment(patient_id: Optional[str], assessment: dict):
    """Persist assessment in memory store."""
    if patient_id:
        if patient_id not in assessment_store:
            assessment_store[patient_id] = []
        assessment_store[patient_id].append(assessment)


# ──────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────

@app.post("/predict", response_model=RiskAssessment)
def predict(features: GaitFeatures):
    """Predict fall risk from pre-extracted gait features."""
    feature_dict = features.model_dump(exclude={"patient_id"})
    predictor = FallRiskPredictor.get_instance()

    try:
        result = predictor.predict_risk(feature_dict)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    assessment = RiskAssessment(
        assessment_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        score=result["score"],
        category=result["category"],
        top_factors=result["top_factors"],
        patient_id=features.patient_id,
    )

    _store_assessment(features.patient_id, assessment.model_dump())
    return assessment


@app.post("/upload-session", response_model=RiskAssessment)
def upload_session(session_data: RawSessionUpload):
    """Upload raw sensor data, extract features, and predict risk."""
    # Convert to numpy arrays
    try:
        fsr = np.array(session_data.fsr, dtype=np.float64)
        imu = np.array(session_data.imu, dtype=np.float64)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid sensor data: {e}")

    if fsr.ndim != 2 or fsr.shape[1] != 8:
        raise HTTPException(status_code=400,
                            detail=f"FSR must have shape (n, 8), got {fsr.shape}")
    if imu.ndim != 2 or imu.shape[1] != 6:
        raise HTTPException(status_code=400,
                            detail=f"IMU must have shape (n, 6), got {imu.shape}")

    # Build session dict for feature extraction
    raw_session = {
        "fsr": fsr,
        "imu": imu,
        "fs": session_data.fs,
        "foot_temperature": session_data.foot_temperature,
    }

    # Extract features
    feature_dict = extract_features(raw_session)

    # Predict
    predictor = FallRiskPredictor.get_instance()
    try:
        result = predictor.predict_risk(feature_dict)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    assessment = RiskAssessment(
        assessment_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        score=result["score"],
        category=result["category"],
        top_factors=result["top_factors"],
        patient_id=session_data.patient_id,
    )

    _store_assessment(session_data.patient_id, assessment.model_dump())
    return assessment


@app.get("/patient/{patient_id}/history", response_model=List[RiskAssessment])
def get_patient_history(patient_id: str):
    """Return historical risk assessments for a patient."""
    if patient_id not in assessment_store:
        raise HTTPException(status_code=404,
                            detail=f"No records found for patient {patient_id}")
    return assessment_store[patient_id]


@app.get("/patient/{patient_id}/report", response_model=PatientReport)
def get_patient_report(patient_id: str):
    """Return a detailed report for a patient."""
    if patient_id not in assessment_store or not assessment_store[patient_id]:
        raise HTTPException(status_code=404,
                            detail=f"No records found for patient {patient_id}")

    records = assessment_store[patient_id]
    scores = [r["score"] for r in records]
    avg_score = float(np.mean(scores))

    # Trend detection
    if len(scores) < 2:
        trend = "stable"
    else:
        recent_half = scores[len(scores) // 2:]
        earlier_half = scores[:len(scores) // 2]
        diff = np.mean(recent_half) - np.mean(earlier_half)
        if diff < -0.05:
            trend = "improving"
        elif diff > 0.05:
            trend = "worsening"
        else:
            trend = "stable"

    return PatientReport(
        patient_id=patient_id,
        total_assessments=len(records),
        latest_score=scores[-1],
        latest_category=records[-1]["category"],
        average_score=round(avg_score, 4),
        trend=trend,
        assessments=records,
    )


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    model_loaded = False
    try:
        predictor = FallRiskPredictor.get_instance()
        predictor._ensure_loaded()
        model_loaded = True
    except Exception:
        pass

    return HealthResponse(
        status="ok",
        model_loaded=model_loaded,
        timestamp=datetime.utcnow().isoformat(),
    )
