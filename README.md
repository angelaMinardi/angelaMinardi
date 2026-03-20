# Smart Insole Fall Prevention System

A comprehensive IoT system that uses a smart insole with force-sensitive resistors (FSRs), an IMU, a temperature sensor, and machine learning to predict fall risk in aging populations.

## Architecture

```
┌─────────────┐     BLE 5.0      ┌──────────────┐     HTTP/WS      ┌─────────────────┐
│ Smart Insole │ ──────────────► │   Web App     │ ──────────────► │  FastAPI Server  │
│  (nRF52840)  │   40B @ 20Hz    │ (React + TS)  │                 │  (XGBoost ML)    │
└─────────────┘                  └──────────────┘                  └─────────────────┘
     │                                │    │                              │
     ├─ 8x FSR 402 (pressure)        │    ├─ Patient Dashboard           ├─ Risk prediction
     ├─ BMI270 IMU (motion)           │    ├─ Clinician Dashboard         ├─ Feature extraction
     ├─ TMP117 (foot temperature)     │    ├─ Pressure Heatmap            ├─ Session storage
     ├─ Battery monitoring            │    └─ PDF Reports                 └─ Patient history
     └─ On-device filtering           │
                                      └─ Web Bluetooth API
```

## Components

### Hardware (`hardware/`)
Flexible PCB insole with 8 FSR sensors at anatomically significant positions, BMI270 IMU, TMP117 temperature sensor, nRF52840 SoC, and LiPo battery management. Supports bilateral (paired left/right) operation for asymmetry analysis. Full design documentation with schematics, BOM, and PCB layout specifications.

### Firmware (`firmware/`)
nRF Connect SDK (Zephyr RTOS) firmware for the nRF52840:
- 100Hz IMU sampling, 50Hz FSR scanning via analog multiplexer
- Periodic temperature monitoring for neuropathy screening
- Custom BLE GATT service streaming 40-byte gait data packets at 20Hz
- Butterworth IIR filtering and on-device gait feature extraction
- Fall detection via free-fall + impact signature with emergency alerts
- Power management targeting 8-12 hour battery life on 150mAh

### ML Pipeline (`ml/`)
Python-based machine learning pipeline:
- Synthetic gait data generator with realistic biomechanical parameters
- 25-30 gait feature extraction (temporal, spatial, pressure, variability)
- XGBoost classifier with SHAP explainability
- Freezing of Gait (FoG) episode detection
- FastAPI server for real-time risk prediction

### Web Application (`app/`)
React + TypeScript dashboard with dual interfaces:
- **Patient view**: Fall risk gauge, 7-day trends, step counter, alerts, recommendations
- **Clinician view**: Patient list, pressure heatmaps, gait analytics, bilateral asymmetry, temporal analysis, PDF reports
- Works standalone with mock data or connected to FastAPI backend

## Quick Start

### ML Pipeline
```bash
cd ml
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate synthetic data and train model
python -m src.data.synthetic
python -m src.models.train
python -m src.models.evaluate

# Start API server
uvicorn src.api.serve:app --reload
```

### Web App
```bash
cd app
npm install
npm run dev          # Standalone with mock data
# or
VITE_API_URL=http://localhost:8000 npm run dev  # With backend
```

### Firmware
```bash
cd firmware
west build -b nrf52840dk_nrf52840
west flash
```

## Hardware BOM Summary

| Component | Part Number | Purpose |
|-----------|-------------|---------|
| MCU | NRF52840-QIAA-R7 | Processor + BLE 5.0 |
| IMU | BMI270 (Bosch) | 6-axis motion, 685uA |
| Temperature | TMP117 (TI) | Foot temperature, neuropathy screening |
| FSR (x8) | Interlink FSR 402 | Plantar pressure mapping |
| Analog MUX | CD74HC4051 (TI) | 8:1 FSR multiplexing |
| Voltage Reg | TPS62740 (TI) | 3.3V, 360nA quiescent |
| Charger | MCP73831 | Single-cell LiPo charging |
| Battery | LiPo 3.7V 150mAh | Thin-profile, heel cavity |

See [`hardware/bom.csv`](hardware/bom.csv) for the complete bill of materials.

## Project Structure

```
├── hardware/           # PCB design documentation
│   ├── schematic.md    # Full circuit schematic
│   ├── pcb-layout.md   # PCB layout specifications
│   ├── bom.csv         # Bill of materials
│   └── design-notes.md # Design rationale
├── firmware/           # nRF52840 Zephyr firmware
│   └── src/            # C source (sensors, BLE, DSP, power)
├── ml/                 # Python ML pipeline
│   ├── src/            # Data, features, models, API
│   └── notebooks/      # Jupyter analysis notebooks
└── app/                # React web application
    └── src/            # Components, hooks, pages, store
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| nRF52840 over ESP32 | ~5mA BLE vs ~130mA -- mandatory for all-day wearable |
| BMI270 over MPU6050 | Lowest power (685uA), built-in step counter, wearable-optimized |
| 8 FSRs at key zones | Research shows 6-8 sensors capture clinically relevant pressure distribution |
| XGBoost over deep learning | Matches/beats DL on tabular gait features, interpretable via SHAP |
| Web app over native | Web Bluetooth covers Chrome/Edge + Android; avoids app store complexity |
| Bilateral support | Left/right asymmetry is one of the strongest fall risk predictors |

## Regulatory Considerations

This device, if commercialized, would likely be classified as an FDA Class II medical device requiring 510(k) clearance. The current implementation is intended as a research prototype and educational project.

## License

MIT
