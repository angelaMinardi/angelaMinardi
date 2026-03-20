"""
Generate realistic synthetic gait data for fall risk prediction.

Produces ~1000 walking bouts with extracted features (CSV) and raw time-series
sessions (pickle) suitable for training a fall-risk classifier.
"""

import os
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

# Reproducibility
RNG = np.random.default_rng(42)

# Paths
DATA_DIR = Path(__file__).resolve().parents[3] / "data"
CSV_PATH = DATA_DIR / "synthetic_gait_data.csv"
PKL_PATH = DATA_DIR / "synthetic_raw_sessions.pkl"

# Sensor constants
FS = 100  # sampling rate (Hz)
DURATION = 10.0  # seconds per bout
N_FSR = 8  # FSR pressure channels
N_IMU = 6  # 3-axis accel + 3-axis gyro

# FSR channel mapping (per foot)
# 0: heel-medial, 1: heel-lateral, 2: midfoot-medial, 3: midfoot-lateral,
# 4: forefoot-medial, 5: forefoot-lateral, 6: toe-medial, 7: toe-lateral

# ──────────────────────────────────────────────────────────────────────
# Helper: generate a single raw gait session (time series)
# ──────────────────────────────────────────────────────────────────────

def _generate_fsr_gait_cycle(n_samples: int, stance_pct: float,
                              peak_heel: float, peak_forefoot: float,
                              peak_toe: float, noise_std: float) -> np.ndarray:
    """Return an (n_samples, 8) FSR array for one gait cycle."""
    t = np.linspace(0, 1, n_samples)
    stance_end = stance_pct
    fsr = np.zeros((n_samples, N_FSR))

    # Heel contact (channels 0-1): ramp up then down in first 30% of stance
    heel_mask = t < stance_end * 0.30
    heel_profile = np.where(heel_mask,
                            peak_heel * np.sin(np.pi * t / (stance_end * 0.30)),
                            0.0)
    fsr[:, 0] = heel_profile * 0.55
    fsr[:, 1] = heel_profile * 0.45

    # Midfoot (channels 2-3): active 15-60% of stance
    mid_start, mid_end = stance_end * 0.15, stance_end * 0.60
    mid_mask = (t >= mid_start) & (t <= mid_end)
    mid_profile = np.where(mid_mask,
                           peak_heel * 0.4 * np.sin(np.pi * (t - mid_start) / (mid_end - mid_start)),
                           0.0)
    fsr[:, 2] = mid_profile * 0.5
    fsr[:, 3] = mid_profile * 0.5

    # Forefoot (channels 4-5): active 40-85% of stance
    ff_start, ff_end = stance_end * 0.40, stance_end * 0.85
    ff_mask = (t >= ff_start) & (t <= ff_end)
    ff_profile = np.where(ff_mask,
                          peak_forefoot * np.sin(np.pi * (t - ff_start) / (ff_end - ff_start)),
                          0.0)
    fsr[:, 4] = ff_profile * 0.55
    fsr[:, 5] = ff_profile * 0.45

    # Toe (channels 6-7): active 70-100% of stance (push-off)
    toe_start, toe_end = stance_end * 0.70, stance_end
    toe_mask = (t >= toe_start) & (t <= toe_end)
    toe_profile = np.where(toe_mask,
                           peak_toe * np.sin(np.pi * (t - toe_start) / (toe_end - toe_start)),
                           0.0)
    fsr[:, 6] = toe_profile * 0.6
    fsr[:, 7] = toe_profile * 0.4

    # Swing phase is zero (already zeros)
    # Add sensor noise
    fsr += RNG.normal(0, noise_std, fsr.shape)
    fsr = np.clip(fsr, 0, None)
    return fsr


def _generate_imu_gait_cycle(n_samples: int, stance_pct: float,
                              stride_length: float, sway_rms: float,
                              noise_std: float) -> np.ndarray:
    """Return an (n_samples, 6) IMU array for one gait cycle.
    Columns: ax, ay, az, gx, gy, gz
    ax=anterior-posterior, ay=medial-lateral, az=vertical
    """
    t = np.linspace(0, 1, n_samples)
    imu = np.zeros((n_samples, N_IMU))

    # Vertical acceleration: double-bump pattern during stance
    stance_mask = t < stance_pct
    az_stance = 9.81 + 2.5 * np.sin(2 * np.pi * t / stance_pct) * stance_mask
    az_swing = 9.81 * np.ones(n_samples) * (~stance_mask)
    imu[:, 2] = az_stance + az_swing * (~stance_mask).astype(float)
    imu[:, 2] = np.where(stance_mask, az_stance, 9.81 - 0.5 * np.sin(np.pi * (t - stance_pct) / (1 - stance_pct)))

    # AP acceleration: related to propulsion/braking
    imu[:, 0] = stride_length * 2.0 * np.sin(2 * np.pi * t) + RNG.normal(0, 0.1, n_samples)

    # ML acceleration: sway component
    imu[:, 1] = sway_rms * np.sqrt(2) * np.sin(2 * np.pi * 0.5 * t + RNG.uniform(0, np.pi)) + \
                RNG.normal(0, sway_rms * 0.3, n_samples)

    # Gyroscope: approximate angular velocities
    imu[:, 3] = 1.5 * np.sin(2 * np.pi * t) + RNG.normal(0, 0.05, n_samples)  # roll
    imu[:, 4] = 2.0 * np.cos(2 * np.pi * t) + RNG.normal(0, 0.05, n_samples)  # pitch
    imu[:, 5] = 0.3 * np.sin(4 * np.pi * t) + RNG.normal(0, 0.02, n_samples)  # yaw

    # Add sensor noise
    imu += RNG.normal(0, noise_std, imu.shape)
    return imu


def generate_raw_session(is_high_risk: bool, session_id: int) -> dict:
    """Generate a full raw session (~10 s at 100 Hz) with labels."""
    n_total = int(FS * DURATION)

    # Gait parameters from published norms (or high-risk deviations)
    if is_high_risk:
        cadence = RNG.uniform(70, 100)  # steps/min (slower)
        stride_length_mean = RNG.uniform(0.6, 1.0)
        stride_length_cv = RNG.uniform(8, 18)  # %
        stance_pct = RNG.uniform(0.62, 0.72)
        peak_heel = RNG.uniform(200, 400)
        peak_forefoot = RNG.uniform(150, 350)
        peak_toe = RNG.uniform(80, 200)
        sway_rms = RNG.uniform(0.8, 2.5)  # m/s^2
        foot_temp = RNG.choice(
            [RNG.uniform(20, 25), RNG.uniform(28, 32)],
            p=[0.6, 0.4]
        )
        noise_std_fsr = RNG.uniform(5, 15)
        noise_std_imu = RNG.uniform(0.05, 0.15)
        pressure_asym = RNG.uniform(0.15, 0.40)
    else:
        cadence = RNG.uniform(100, 120)
        stride_length_mean = RNG.uniform(1.2, 1.5)
        stride_length_cv = RNG.uniform(2, 7)  # %
        stance_pct = RNG.uniform(0.58, 0.63)
        peak_heel = RNG.uniform(300, 600)
        peak_forefoot = RNG.uniform(250, 500)
        peak_toe = RNG.uniform(150, 350)
        sway_rms = RNG.uniform(0.2, 0.7)
        foot_temp = RNG.uniform(28, 32)
        noise_std_fsr = RNG.uniform(2, 8)
        noise_std_imu = RNG.uniform(0.02, 0.06)
        pressure_asym = RNG.uniform(0.02, 0.12)

    step_time = 60.0 / cadence  # seconds per step
    stride_time = 2 * step_time
    samples_per_stride = int(stride_time * FS)
    if samples_per_stride < 20:
        samples_per_stride = 20

    n_strides = max(1, n_total // samples_per_stride)

    # Build full session by concatenating gait cycles with variability
    fsr_all = []
    imu_all = []
    stride_lengths = []

    for i in range(n_strides):
        # Add stride-to-stride variability
        sl_var = stride_length_mean * (1 + RNG.normal(0, stride_length_cv / 100))
        stride_lengths.append(sl_var)
        sp_var = stance_pct + RNG.normal(0, 0.01 if not is_high_risk else 0.03)
        sp_var = np.clip(sp_var, 0.50, 0.80)

        n_samp = samples_per_stride + int(RNG.normal(0, 3))
        n_samp = max(20, min(n_samp, samples_per_stride + 20))

        fsr_cycle = _generate_fsr_gait_cycle(n_samp, sp_var,
                                              peak_heel, peak_forefoot,
                                              peak_toe, noise_std_fsr)
        # Apply asymmetry to medial/lateral channels
        asym_factor = 1.0 + pressure_asym * RNG.choice([-1, 1])
        fsr_cycle[:, [0, 2, 4, 6]] *= asym_factor
        fsr_cycle[:, [1, 3, 5, 7]] *= (2 - asym_factor)

        imu_cycle = _generate_imu_gait_cycle(n_samp, sp_var, sl_var,
                                              sway_rms, noise_std_imu)
        fsr_all.append(fsr_cycle)
        imu_all.append(imu_cycle)

    fsr_data = np.concatenate(fsr_all, axis=0)[:n_total]
    imu_data = np.concatenate(imu_all, axis=0)[:n_total]

    # Pad if shorter than expected
    if fsr_data.shape[0] < n_total:
        pad_len = n_total - fsr_data.shape[0]
        fsr_data = np.vstack([fsr_data, np.zeros((pad_len, N_FSR))])
        imu_data = np.vstack([imu_data, np.zeros((pad_len, N_IMU))])

    return {
        "session_id": session_id,
        "label": int(is_high_risk),
        "fs": FS,
        "duration": DURATION,
        "fsr": fsr_data,  # (n_total, 8)
        "imu": imu_data,  # (n_total, 6)
        "foot_temperature": foot_temp,
        "params": {
            "cadence": cadence,
            "stride_length_mean": stride_length_mean,
            "stride_length_cv": stride_length_cv,
            "stance_pct": stance_pct,
            "sway_rms": sway_rms,
            "pressure_asym": pressure_asym,
        }
    }


# ──────────────────────────────────────────────────────────────────────
# Extract summary features from a raw session (for the CSV dataset)
# ──────────────────────────────────────────────────────────────────────

def _extract_features_from_params(session: dict) -> dict:
    """Quick feature extraction using known generation parameters + measured signals."""
    p = session["params"]
    fsr = session["fsr"]
    imu = session["imu"]
    fs = session["fs"]

    cadence = p["cadence"]
    step_time_mean = 60.0 / cadence
    stride_time_mean = 2 * step_time_mean
    stride_time_cv = p["stride_length_cv"] * RNG.uniform(0.8, 1.2)
    step_time_cv = stride_time_cv * RNG.uniform(0.9, 1.1)

    stance_pct = p["stance_pct"] * 100
    swing_pct = 100 - stance_pct
    double_support_pct = (stance_pct - 50) * 2  # approximate

    stride_length_mean = p["stride_length_mean"]
    stride_length_cv = p["stride_length_cv"]
    walking_speed = stride_length_mean * cadence / 120.0

    # Pressure features from FSR data
    peak_heel = np.percentile(fsr[:, 0] + fsr[:, 1], 95)
    peak_midfoot = np.percentile(fsr[:, 2] + fsr[:, 3], 95)
    peak_forefoot = np.percentile(fsr[:, 4] + fsr[:, 5], 95)
    peak_toe = np.percentile(fsr[:, 6] + fsr[:, 7], 95)

    # Center of pressure displacement
    total_force = fsr.sum(axis=1) + 1e-9
    # AP COP: weighted position along foot (heel=0, toe=1)
    positions_ap = np.array([0.0, 0.0, 0.3, 0.3, 0.6, 0.6, 0.9, 0.9])
    cop_ap = (fsr * positions_ap).sum(axis=1) / total_force
    cop_displacement_ap = np.std(cop_ap) * 100  # in mm-equivalent

    # ML COP: medial(0) vs lateral(1)
    positions_ml = np.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0])
    cop_ml = (fsr * positions_ml).sum(axis=1) / total_force
    cop_displacement_ml = np.std(cop_ml) * 100

    # Pressure symmetry index
    medial_sum = fsr[:, [0, 2, 4, 6]].sum()
    lateral_sum = fsr[:, [1, 3, 5, 7]].sum()
    pressure_symmetry_index = abs(medial_sum - lateral_sum) / (medial_sum + lateral_sum + 1e-9) * 100

    # Heel-to-toe transfer time (rough estimate from peak timings)
    heel_signal = fsr[:, 0] + fsr[:, 1]
    toe_signal = fsr[:, 6] + fsr[:, 7]
    heel_peak_idx = np.argmax(heel_signal[:len(heel_signal) // 2]) if heel_signal.max() > 0 else 0
    toe_peak_idx = np.argmax(toe_signal[len(toe_signal) // 2:]) + len(toe_signal) // 2 if toe_signal.max() > 0 else len(toe_signal) - 1
    heel_to_toe_transfer_time = (toe_peak_idx - heel_peak_idx) / fs

    total_grf = np.mean(total_force)

    # Variability
    stride_variability_index = stride_length_cv + stride_time_cv * 0.5

    # COP path length
    cop_ap_diff = np.diff(cop_ap)
    cop_ml_diff = np.diff(cop_ml)
    cop_path_length = np.sum(np.sqrt(cop_ap_diff**2 + cop_ml_diff**2)) * 10

    # Sway RMS from ML acceleration
    ay = imu[:, 1]
    sway_rms = np.sqrt(np.mean(ay**2))

    # Step count
    step_count = int(cadence * (session["duration"] / 60.0))

    return {
        "stride_time_mean": round(stride_time_mean, 4),
        "stride_time_cv": round(stride_time_cv, 2),
        "step_time_mean": round(step_time_mean, 4),
        "step_time_cv": round(step_time_cv, 2),
        "stance_phase_pct": round(stance_pct, 2),
        "swing_phase_pct": round(swing_pct, 2),
        "double_support_pct": round(double_support_pct, 2),
        "cadence": round(cadence, 2),
        "stride_length_mean": round(stride_length_mean, 4),
        "stride_length_cv": round(stride_length_cv, 2),
        "walking_speed": round(walking_speed, 4),
        "peak_pressure_heel": round(peak_heel, 2),
        "peak_pressure_midfoot": round(peak_midfoot, 2),
        "peak_pressure_forefoot": round(peak_forefoot, 2),
        "peak_pressure_toe": round(peak_toe, 2),
        "cop_displacement_ap": round(cop_displacement_ap, 4),
        "cop_displacement_ml": round(cop_displacement_ml, 4),
        "pressure_symmetry_index": round(pressure_symmetry_index, 4),
        "heel_to_toe_transfer_time": round(heel_to_toe_transfer_time, 4),
        "total_ground_reaction_force": round(total_grf, 2),
        "stride_variability_index": round(stride_variability_index, 4),
        "cop_path_length": round(cop_path_length, 4),
        "sway_rms": round(sway_rms, 4),
        "foot_temperature": round(session["foot_temperature"], 2),
        "step_count": step_count,
    }


# ──────────────────────────────────────────────────────────────────────
# Main generation routine
# ──────────────────────────────────────────────────────────────────────

def generate_dataset(n_bouts: int = 1000, high_risk_frac: float = 0.30):
    """Generate the full synthetic dataset.

    Returns
    -------
    features_df : pd.DataFrame  – extracted features with 'label' column
    raw_sessions : list[dict]   – raw time-series sessions
    """
    labels = RNG.random(n_bouts) < high_risk_frac
    raw_sessions = []
    feature_rows = []

    for i in range(n_bouts):
        session = generate_raw_session(bool(labels[i]), session_id=i)
        raw_sessions.append(session)
        feats = _extract_features_from_params(session)
        feats["label"] = session["label"]
        feats["session_id"] = i
        feature_rows.append(feats)

    features_df = pd.DataFrame(feature_rows)
    return features_df, raw_sessions


def save_dataset(features_df: pd.DataFrame, raw_sessions: list):
    """Persist datasets to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(CSV_PATH, index=False)
    with open(PKL_PATH, "wb") as f:
        pickle.dump(raw_sessions, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Saved features CSV  -> {CSV_PATH}  ({len(features_df)} rows)")
    print(f"Saved raw sessions  -> {PKL_PATH}  ({len(raw_sessions)} sessions)")


def print_summary(features_df: pd.DataFrame):
    """Print dataset summary statistics."""
    print("\n" + "=" * 60)
    print("SYNTHETIC GAIT DATASET SUMMARY")
    print("=" * 60)
    print(f"Total bouts: {len(features_df)}")
    label_counts = features_df["label"].value_counts().sort_index()
    print(f"  Low risk  (0): {label_counts.get(0, 0)} ({label_counts.get(0, 0)/len(features_df)*100:.1f}%)")
    print(f"  High risk (1): {label_counts.get(1, 0)} ({label_counts.get(1, 0)/len(features_df)*100:.1f}%)")
    print(f"\nFeature columns ({len(features_df.columns) - 2}):")
    feature_cols = [c for c in features_df.columns if c not in ("label", "session_id")]
    for col in feature_cols:
        print(f"  {col:35s}  mean={features_df[col].mean():10.3f}  std={features_df[col].std():10.3f}")
    print()
    print("Per-class means for key features:")
    key_features = ["cadence", "stride_length_mean", "stride_length_cv",
                    "walking_speed", "sway_rms", "foot_temperature",
                    "pressure_symmetry_index"]
    for feat in key_features:
        low = features_df.loc[features_df["label"] == 0, feat].mean()
        high = features_df.loc[features_df["label"] == 1, feat].mean()
        print(f"  {feat:35s}  low_risk={low:8.3f}  high_risk={high:8.3f}")
    print("=" * 60)


# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    features_df, raw_sessions = generate_dataset(n_bouts=1000, high_risk_frac=0.30)
    save_dataset(features_df, raw_sessions)
    print_summary(features_df)
