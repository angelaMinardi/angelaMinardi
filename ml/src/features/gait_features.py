"""
Gait feature extraction pipeline for the Smart Insole system.

Extracts ~25 features from raw FSR (8 channels) and IMU (6-axis) data
for each walking bout / session.
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, butter, filtfilt
from typing import Dict, List, Optional


# FSR channel indices
HEEL_MEDIAL, HEEL_LATERAL = 0, 1
MIDFOOT_MEDIAL, MIDFOOT_LATERAL = 2, 3
FOREFOOT_MEDIAL, FOREFOOT_LATERAL = 4, 5
TOE_MEDIAL, TOE_LATERAL = 6, 7

# Anatomical AP positions (normalised 0=heel, 1=toe)
AP_POSITIONS = np.array([0.0, 0.0, 0.3, 0.3, 0.6, 0.6, 0.9, 0.9])
# Medial (0) / Lateral (1) indicator
ML_POSITIONS = np.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0])

FEATURE_NAMES = [
    "stride_time_mean", "stride_time_cv",
    "step_time_mean", "step_time_cv",
    "stance_phase_pct", "swing_phase_pct",
    "double_support_pct",
    "cadence",
    "stride_length_mean", "stride_length_cv",
    "walking_speed",
    "peak_pressure_heel", "peak_pressure_midfoot",
    "peak_pressure_forefoot", "peak_pressure_toe",
    "cop_displacement_ap", "cop_displacement_ml",
    "pressure_symmetry_index",
    "heel_to_toe_transfer_time",
    "total_ground_reaction_force",
    "stride_variability_index",
    "cop_path_length",
    "sway_rms",
    "foot_temperature",
    "step_count",
]


# ──────────────────────────────────────────────────────────────────────
# Heel-strike / Toe-off detection from FSR
# ──────────────────────────────────────────────────────────────────────

def _detect_heel_strikes(fsr: np.ndarray, fs: float) -> np.ndarray:
    """Detect heel-strike events from combined heel FSR channels.

    Returns array of sample indices where heel strikes occur.
    """
    heel_signal = fsr[:, HEEL_MEDIAL] + fsr[:, HEEL_LATERAL]

    # Adaptive threshold: 20% of max heel pressure
    threshold = 0.20 * np.max(heel_signal) if np.max(heel_signal) > 0 else 0.1
    min_distance = int(0.4 * fs)  # minimum 400 ms between strikes

    peaks, _ = find_peaks(heel_signal, height=threshold,
                          distance=min_distance, prominence=threshold * 0.3)
    return peaks


def _detect_toe_offs(fsr: np.ndarray, fs: float) -> np.ndarray:
    """Detect toe-off events from combined toe FSR channels.

    Returns array of sample indices where toe-off occurs (signal drops).
    """
    toe_signal = fsr[:, TOE_MEDIAL] + fsr[:, TOE_LATERAL]

    # Toe-off is when toe pressure drops; detect negative peaks (inverted)
    threshold = 0.20 * np.max(toe_signal) if np.max(toe_signal) > 0 else 0.1
    min_distance = int(0.4 * fs)

    # Find peaks in the toe signal (these mark peak push-off just before toe-off)
    peaks, _ = find_peaks(toe_signal, height=threshold,
                          distance=min_distance, prominence=threshold * 0.3)
    return peaks


# ──────────────────────────────────────────────────────────────────────
# Stride length estimation via double integration + ZUPT
# ──────────────────────────────────────────────────────────────────────

def _estimate_stride_lengths(imu: np.ndarray, fs: float,
                              heel_strikes: np.ndarray) -> np.ndarray:
    """Estimate stride lengths from IMU AP acceleration using
    zero-velocity update (ZUPT) constrained double integration.

    Parameters
    ----------
    imu : (n, 6) array – [ax, ay, az, gx, gy, gz]
    fs  : sampling rate
    heel_strikes : indices of heel strikes

    Returns
    -------
    Array of estimated stride lengths (meters).
    """
    ax = imu[:, 0]  # anterior-posterior acceleration
    dt = 1.0 / fs
    stride_lengths = []

    for i in range(len(heel_strikes) - 1):
        s0 = heel_strikes[i]
        s1 = heel_strikes[i + 1]
        if s1 - s0 < 10:
            continue

        seg = ax[s0:s1].copy()

        # Remove mean (drift correction)
        seg -= np.mean(seg)

        # First integration -> velocity
        vel = np.cumsum(seg) * dt
        # ZUPT: linearly ramp velocity so it starts and ends at zero
        vel -= np.linspace(vel[0], vel[-1], len(vel))

        # Second integration -> displacement
        disp = np.cumsum(vel) * dt
        # Stride length is total forward displacement
        sl = abs(disp[-1] - disp[0])
        # Clamp to reasonable range
        sl = np.clip(sl, 0.2, 3.0)
        stride_lengths.append(sl)

    if not stride_lengths:
        return np.array([1.0])  # default fallback
    return np.array(stride_lengths)


# ──────────────────────────────────────────────────────────────────────
# Main feature extraction
# ──────────────────────────────────────────────────────────────────────

def extract_features(raw_session: dict) -> Dict[str, float]:
    """Extract all gait features from a single raw session / bout.

    Parameters
    ----------
    raw_session : dict
        Required keys: 'fsr' (n,8), 'imu' (n,6), 'fs' (float),
        'foot_temperature' (float).

    Returns
    -------
    dict with ~25 named features.
    """
    fsr = np.asarray(raw_session["fsr"], dtype=np.float64)
    imu = np.asarray(raw_session["imu"], dtype=np.float64)
    fs = float(raw_session["fs"])
    foot_temp = float(raw_session.get("foot_temperature", 30.0))
    n_samples = fsr.shape[0]
    duration_s = n_samples / fs

    # ── Temporal features from FSR ──────────────────────────────────
    heel_strikes = _detect_heel_strikes(fsr, fs)
    toe_offs = _detect_toe_offs(fsr, fs)

    # Stride times (heel-strike to heel-strike)
    if len(heel_strikes) >= 2:
        stride_times = np.diff(heel_strikes) / fs
        stride_time_mean = float(np.mean(stride_times))
        stride_time_cv = float(np.std(stride_times) / (np.mean(stride_times) + 1e-9) * 100)
    else:
        stride_time_mean = duration_s
        stride_time_cv = 0.0

    # Step times (half of stride for single-foot sensor)
    step_times = stride_times / 2 if len(heel_strikes) >= 2 else np.array([duration_s / 2])
    step_time_mean = float(np.mean(step_times))
    step_time_cv = float(np.std(step_times) / (np.mean(step_times) + 1e-9) * 100)

    # Stance / swing phase estimation
    # Stance = time when total FSR > threshold
    total_fsr = fsr.sum(axis=1)
    fsr_threshold = 0.1 * np.max(total_fsr) if np.max(total_fsr) > 0 else 0
    stance_samples = np.sum(total_fsr > fsr_threshold)
    stance_phase_pct = float(stance_samples / n_samples * 100)
    swing_phase_pct = 100.0 - stance_phase_pct

    # Double support % (approximate: stance% * 2 - 100, clamped)
    double_support_pct = max(0.0, (stance_phase_pct - 50.0) * 2)

    # Cadence
    n_steps = max(1, len(heel_strikes))
    cadence = float(n_steps / duration_s * 60)

    # Step count
    step_count = int(n_steps)

    # ── Spatial features from IMU ───────────────────────────────────
    stride_lengths = _estimate_stride_lengths(imu, fs, heel_strikes)
    stride_length_mean = float(np.mean(stride_lengths))
    stride_length_cv = float(np.std(stride_lengths) / (np.mean(stride_lengths) + 1e-9) * 100)
    walking_speed = float(stride_length_mean / (stride_time_mean + 1e-9))

    # ── Pressure features from FSR ──────────────────────────────────
    peak_pressure_heel = float(np.percentile(fsr[:, HEEL_MEDIAL] + fsr[:, HEEL_LATERAL], 95))
    peak_pressure_midfoot = float(np.percentile(fsr[:, MIDFOOT_MEDIAL] + fsr[:, MIDFOOT_LATERAL], 95))
    peak_pressure_forefoot = float(np.percentile(fsr[:, FOREFOOT_MEDIAL] + fsr[:, FOREFOOT_LATERAL], 95))
    peak_pressure_toe = float(np.percentile(fsr[:, TOE_MEDIAL] + fsr[:, TOE_LATERAL], 95))

    # Center of pressure
    total_force = fsr.sum(axis=1) + 1e-9
    cop_ap = (fsr * AP_POSITIONS).sum(axis=1) / total_force
    cop_ml = (fsr * ML_POSITIONS).sum(axis=1) / total_force

    cop_displacement_ap = float(np.std(cop_ap) * 100)  # mm-equivalent units
    cop_displacement_ml = float(np.std(cop_ml) * 100)

    # Pressure symmetry index
    medial_total = fsr[:, [HEEL_MEDIAL, MIDFOOT_MEDIAL, FOREFOOT_MEDIAL, TOE_MEDIAL]].sum()
    lateral_total = fsr[:, [HEEL_LATERAL, MIDFOOT_LATERAL, FOREFOOT_LATERAL, TOE_LATERAL]].sum()
    pressure_symmetry_index = float(
        abs(medial_total - lateral_total) / (medial_total + lateral_total + 1e-9) * 100
    )

    # Heel to toe transfer time
    heel_signal = fsr[:, HEEL_MEDIAL] + fsr[:, HEEL_LATERAL]
    toe_signal = fsr[:, TOE_MEDIAL] + fsr[:, TOE_LATERAL]
    half = n_samples // 2
    heel_peak_idx = int(np.argmax(heel_signal[:half])) if heel_signal.max() > 0 else 0
    toe_peak_idx = int(np.argmax(toe_signal[half:])) + half if toe_signal.max() > 0 else n_samples - 1
    heel_to_toe_transfer_time = float((toe_peak_idx - heel_peak_idx) / fs)

    # Total GRF (mean)
    total_ground_reaction_force = float(np.mean(total_force))

    # ── Variability features ────────────────────────────────────────
    stride_variability_index = float(stride_length_cv + stride_time_cv * 0.5)

    # COP path length
    cop_ap_diff = np.diff(cop_ap)
    cop_ml_diff = np.diff(cop_ml)
    cop_path_length = float(np.sum(np.sqrt(cop_ap_diff ** 2 + cop_ml_diff ** 2)) * 10)

    # Sway RMS from medial-lateral acceleration
    ay = imu[:, 1]
    sway_rms = float(np.sqrt(np.mean(ay ** 2)))

    return {
        "stride_time_mean": round(stride_time_mean, 4),
        "stride_time_cv": round(stride_time_cv, 2),
        "step_time_mean": round(step_time_mean, 4),
        "step_time_cv": round(step_time_cv, 2),
        "stance_phase_pct": round(stance_phase_pct, 2),
        "swing_phase_pct": round(swing_phase_pct, 2),
        "double_support_pct": round(double_support_pct, 2),
        "cadence": round(cadence, 2),
        "stride_length_mean": round(stride_length_mean, 4),
        "stride_length_cv": round(stride_length_cv, 2),
        "walking_speed": round(walking_speed, 4),
        "peak_pressure_heel": round(peak_pressure_heel, 2),
        "peak_pressure_midfoot": round(peak_pressure_midfoot, 2),
        "peak_pressure_forefoot": round(peak_pressure_forefoot, 2),
        "peak_pressure_toe": round(peak_pressure_toe, 2),
        "cop_displacement_ap": round(cop_displacement_ap, 4),
        "cop_displacement_ml": round(cop_displacement_ml, 4),
        "pressure_symmetry_index": round(pressure_symmetry_index, 4),
        "heel_to_toe_transfer_time": round(heel_to_toe_transfer_time, 4),
        "total_ground_reaction_force": round(total_ground_reaction_force, 2),
        "stride_variability_index": round(stride_variability_index, 4),
        "cop_path_length": round(cop_path_length, 4),
        "sway_rms": round(sway_rms, 4),
        "foot_temperature": round(foot_temp, 2),
        "step_count": step_count,
    }


def extract_features_batch(sessions: list) -> pd.DataFrame:
    """Extract features from multiple sessions / bouts.

    Parameters
    ----------
    sessions : list of dict
        Each dict must have keys: 'fsr', 'imu', 'fs', 'foot_temperature'.
        Optionally 'label' and 'session_id'.

    Returns
    -------
    pd.DataFrame with one row per session and feature columns.
    """
    rows = []
    for session in sessions:
        feats = extract_features(session)
        # Carry over metadata
        if "label" in session:
            feats["label"] = session["label"]
        if "session_id" in session:
            feats["session_id"] = session["session_id"]
        rows.append(feats)
    return pd.DataFrame(rows)
