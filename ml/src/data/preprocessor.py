"""
Preprocessing pipeline for raw insole sensor sessions.

- Segment walking bouts via IMU magnitude thresholding
- Bandpass filter (0.5-25 Hz Butterworth)
- Normalize IMU (remove gravity from accelerometer)
- Handle missing values
"""

import numpy as np
from scipy.signal import butter, filtfilt
from typing import List, Dict, Optional


# ──────────────────────────────────────────────────────────────────────
# Butterworth bandpass filter
# ──────────────────────────────────────────────────────────────────────

def _butter_bandpass(lowcut: float, highcut: float, fs: float, order: int = 4):
    """Design a Butterworth bandpass filter."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    # Clamp to valid range (0, 1)
    low = max(low, 0.001)
    high = min(high, 0.999)
    b, a = butter(order, [low, high], btype="band")
    return b, a


def bandpass_filter(data: np.ndarray, lowcut: float = 0.5,
                    highcut: float = 25.0, fs: float = 100.0,
                    order: int = 4) -> np.ndarray:
    """Apply zero-phase Butterworth bandpass filter to each column.

    Parameters
    ----------
    data : np.ndarray
        Shape (n_samples,) or (n_samples, n_channels).
    lowcut, highcut : float
        Band edges in Hz.
    fs : float
        Sampling frequency.
    order : int
        Filter order.

    Returns
    -------
    np.ndarray – filtered data, same shape as input.
    """
    b, a = _butter_bandpass(lowcut, highcut, fs, order)
    if data.ndim == 1:
        # Need sufficient length for filtfilt
        if len(data) < 3 * max(len(a), len(b)):
            return data.copy()
        return filtfilt(b, a, data)
    else:
        out = np.empty_like(data)
        min_len = 3 * max(len(a), len(b))
        for ch in range(data.shape[1]):
            if data.shape[0] < min_len:
                out[:, ch] = data[:, ch]
            else:
                out[:, ch] = filtfilt(b, a, data[:, ch])
        return out


# ──────────────────────────────────────────────────────────────────────
# IMU normalisation (remove gravity from accelerometer)
# ──────────────────────────────────────────────────────────────────────

def remove_gravity(imu: np.ndarray, fs: float = 100.0) -> np.ndarray:
    """Remove gravity component from accelerometer channels.

    Assumes imu columns are [ax, ay, az, gx, gy, gz].
    Gravity is estimated as the low-frequency component (< 0.5 Hz)
    of each accelerometer axis.

    Parameters
    ----------
    imu : np.ndarray, shape (n, 6)
    fs  : float

    Returns
    -------
    np.ndarray, shape (n, 6) – accel channels have gravity removed,
                                 gyro channels unchanged.
    """
    out = imu.copy()
    # Use a low-pass filter to estimate gravity
    nyq = 0.5 * fs
    cutoff = 0.5 / nyq
    cutoff = max(cutoff, 0.001)
    cutoff = min(cutoff, 0.999)
    b, a = butter(2, cutoff, btype="low")

    min_len = 3 * max(len(a), len(b))
    for ch in range(3):  # only accelerometer axes
        if imu.shape[0] >= min_len:
            gravity_est = filtfilt(b, a, imu[:, ch])
            out[:, ch] = imu[:, ch] - gravity_est
        else:
            # Too short; subtract mean as rough gravity estimate
            out[:, ch] = imu[:, ch] - np.mean(imu[:, ch])
    return out


# ──────────────────────────────────────────────────────────────────────
# Segment walking bouts from continuous data
# ──────────────────────────────────────────────────────────────────────

def detect_walking_bouts(imu: np.ndarray, fs: float = 100.0,
                         accel_threshold: float = 1.0,
                         min_bout_seconds: float = 2.0) -> List[tuple]:
    """Detect motion on/off from IMU accelerometer magnitude.

    Parameters
    ----------
    imu : np.ndarray, shape (n, 6)
    fs  : float
    accel_threshold : float
        Magnitude of dynamic acceleration (gravity removed) above which
        the subject is considered walking.
    min_bout_seconds : float
        Minimum bout duration to keep.

    Returns
    -------
    List of (start_idx, end_idx) tuples for each detected walking bout.
    """
    # Dynamic acceleration magnitude (gravity ≈ 9.81 on az)
    accel = imu[:, :3].copy()
    # Rough gravity removal: subtract column means
    accel_dynamic = accel - accel.mean(axis=0)
    mag = np.sqrt(np.sum(accel_dynamic ** 2, axis=1))

    # Smooth with a short moving average
    win = int(0.1 * fs)  # 100 ms window
    if win < 1:
        win = 1
    kernel = np.ones(win) / win
    mag_smooth = np.convolve(mag, kernel, mode="same")

    walking = mag_smooth > accel_threshold
    min_samples = int(min_bout_seconds * fs)

    bouts = []
    in_bout = False
    start = 0
    for i in range(len(walking)):
        if walking[i] and not in_bout:
            start = i
            in_bout = True
        elif not walking[i] and in_bout:
            if (i - start) >= min_samples:
                bouts.append((start, i))
            in_bout = False
    # Handle case where walking continues to end
    if in_bout and (len(walking) - start) >= min_samples:
        bouts.append((start, len(walking)))

    # If no bouts detected, return the whole session as one bout
    if not bouts:
        bouts = [(0, len(walking))]

    return bouts


# ──────────────────────────────────────────────────────────────────────
# Handle missing values
# ──────────────────────────────────────────────────────────────────────

def handle_missing(data: np.ndarray) -> np.ndarray:
    """Replace NaN/Inf values using linear interpolation, then forward/back fill.

    Parameters
    ----------
    data : np.ndarray, shape (n,) or (n, channels)

    Returns
    -------
    np.ndarray – cleaned data with no NaN/Inf.
    """
    data = data.copy().astype(np.float64)
    data[~np.isfinite(data)] = np.nan

    if data.ndim == 1:
        data = _interpolate_1d(data)
    else:
        for ch in range(data.shape[1]):
            data[:, ch] = _interpolate_1d(data[:, ch])
    return data


def _interpolate_1d(arr: np.ndarray) -> np.ndarray:
    """Linear-interpolate NaN gaps in a 1-D array."""
    nans = np.isnan(arr)
    if not nans.any():
        return arr
    if nans.all():
        return np.zeros_like(arr)
    x = np.arange(len(arr))
    arr[nans] = np.interp(x[nans], x[~nans], arr[~nans])
    return arr


# ──────────────────────────────────────────────────────────────────────
# Full preprocessing pipeline for a single session
# ──────────────────────────────────────────────────────────────────────

def preprocess_session(session: dict) -> List[dict]:
    """Run the full preprocessing pipeline on a raw session.

    Steps:
    1. Handle missing values in FSR and IMU data.
    2. Detect walking bouts from IMU.
    3. Bandpass-filter FSR and IMU for each bout.
    4. Remove gravity from IMU accelerometer channels.

    Parameters
    ----------
    session : dict
        Must contain keys: 'fsr' (n,8), 'imu' (n,6), 'fs', 'label',
        'session_id', 'foot_temperature'.

    Returns
    -------
    List of dicts, one per detected walking bout, each with keys:
        'fsr', 'imu', 'fs', 'label', 'session_id', 'foot_temperature',
        'bout_start', 'bout_end'.
    """
    fsr = handle_missing(session["fsr"])
    imu = handle_missing(session["imu"])
    fs = session["fs"]

    bouts_indices = detect_walking_bouts(imu, fs)

    segments = []
    for start, end in bouts_indices:
        fsr_seg = fsr[start:end]
        imu_seg = imu[start:end]

        # Bandpass filter
        fsr_seg = bandpass_filter(fsr_seg, lowcut=0.5, highcut=25.0, fs=fs)
        imu_seg = bandpass_filter(imu_seg, lowcut=0.5, highcut=25.0, fs=fs)

        # Ensure FSR non-negative after filtering
        fsr_seg = np.clip(fsr_seg, 0, None)

        # Remove gravity from IMU
        imu_seg = remove_gravity(imu_seg, fs)

        segments.append({
            "fsr": fsr_seg,
            "imu": imu_seg,
            "fs": fs,
            "label": session.get("label"),
            "session_id": session.get("session_id"),
            "foot_temperature": session.get("foot_temperature"),
            "bout_start": start,
            "bout_end": end,
        })

    return segments


def preprocess_all(sessions: list) -> List[dict]:
    """Preprocess a list of raw sessions, returning all walking-bout segments."""
    all_segments = []
    for session in sessions:
        segs = preprocess_session(session)
        all_segments.extend(segs)
    return all_segments
