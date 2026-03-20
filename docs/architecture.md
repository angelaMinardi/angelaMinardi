# System Architecture

## Overview

The Smart Insole Fall Prevention System consists of four main subsystems that work together to collect gait data, analyze it, predict fall risk, and present actionable information to patients and clinicians.

```
                        SYSTEM ARCHITECTURE

  +------------------+        +------------------+        +------------------+
  |   SMART INSOLE   |  BLE   |    WEB APP       |  HTTP  |   ML BACKEND     |
  |   (Hardware)     |------->|   (React/TS)     |------->|   (FastAPI)      |
  +------------------+        +------------------+        +------------------+
  |                  |        |                  |        |                  |
  | nRF52840 MCU     |        | Patient View     |        | Feature Extract  |
  | BMI270 IMU       |        |  - Risk Gauge    |        | XGBoost Model    |
  | 8x FSR 402       |        |  - Trends        |        | SHAP Explain     |
  | TMP117 Temp      |        |  - Alerts        |        | Risk Scoring     |
  | CD74HC4051 MUX   |        |  - Steps         |        |                  |
  | BLE 5.0          |        |                  |        | Patient Storage  |
  | LiPo Battery     |        | Clinician View   |        | Report Gen       |
  |                  |        |  - Patient List  |        |                  |
  | Signal Filtering |        |  - Heatmap       |        | REST API:        |
  | Gait Detection   |        |  - Analytics     |        |  POST /predict   |
  | Power Management |        |  - Temporal      |        |  POST /upload    |
  |                  |        |  - PDF Export    |        |  GET /history    |
  +------------------+        +------------------+        +------------------+
         |                           |
         |                    Web Bluetooth API
         +---------------------------+
              40-byte packets @ 20Hz
```

## Data Flow

### 1. Sensor Acquisition (Firmware)

```
FSR Array (8 zones)     IMU (BMI270)          TMP117
     |                       |                   |
     v                       v                   v
 ADC + MUX              SPI Burst Read       I2C Read
 (50 Hz)                (100 Hz)             (0.1 Hz)
     |                       |                   |
     +--------+--------------+-------------------+
              |
              v
      Butterworth IIR Filter
      (20Hz LP for FSR, 50Hz LP for IMU)
              |
              v
      Sensor Manager (Ring Buffer)
              |
              v
      BLE GATT Notify (20 Hz)
```

### 2. BLE Packet Structure (40 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Packet ID             |           Timestamp (ms)      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Timestamp (cont.)       |         FSR[0] Heel Center    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        FSR[1] Heel Med        |        FSR[2] Heel Lat        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|      FSR[3] Midfoot Arch      |       FSR[4] Meta 1st         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       FSR[5] Meta 3rd         |       FSR[6] Meta 5th         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       FSR[7] Big Toe          |         Accel X (mg)          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Accel Y               |         Accel Z               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Gyro X (mdps)         |         Gyro Y                |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Gyro Z                |        Step Count             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Battery % | Status  |         CRC-16                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 3. ML Pipeline

```
Raw Sensor Data (from BLE or file)
         |
         v
   Preprocessing
   - Bandpass filter (0.5-25 Hz)
   - Gravity removal (accelerometer)
   - Walking bout segmentation
         |
         v
   Feature Extraction (25 features)
   - Temporal: stride time, cadence, stance/swing phase
   - Spatial: stride length, walking speed
   - Pressure: CoP displacement, symmetry, peak pressures
   - Variability: stride CV, CoP path length, sway RMS
   - Other: foot temperature, step count
         |
         v
   XGBoost Classifier
   - Binary classification (low risk vs high risk)
   - Probability output 0.0 - 1.0
   - SHAP values for top contributing factors
         |
         v
   Risk Assessment
   - Score: 0-100
   - Category: Low (<30) | Moderate (30-70) | High (>70)
   - Top 3 contributing factors (SHAP-derived)
```

### 4. Web Application Routing

```
  /                    --> LoginPage (role selection)
  /patient             --> PatientDashboard
                            - RiskGauge (circular score display)
                            - AlertBanner (risk-appropriate alerts)
                            - TrendChart (7-day risk history)
                            - DailyTrends (step count bar chart)
                            - Recommendations (actionable advice)
  /clinician           --> ClinicianDashboard
                            - PatientList (sortable table)
                            - RiskGauge + Key Metrics
                            - PressureHeatmap (SVG foot visualization)
                            - GaitAnalytics (bar chart vs norms)
                            - TemporalAnalysis (time series + Poincare)
                            - ReportExport (PDF generation)
```

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| MCU | nRF52840 | Ultra-low BLE power (~5mA), 12-bit ADC |
| RTOS | Zephyr (nRF Connect SDK) | Production BLE stack, power management |
| IMU | BMI270 | Lowest power 6-axis (685uA), wearable-optimized |
| Pressure | Interlink FSR 402 x8 | Proven in gait research, cost-effective |
| Temperature | TMP117 | High accuracy (+/-0.1C), I2C, low power |
| ML Framework | XGBoost + SHAP | Best for tabular gait features, interpretable |
| API | FastAPI | Async Python, auto-docs, Pydantic validation |
| Frontend | React 18 + TypeScript | Type-safe, component-based, Web Bluetooth |
| Charts | Recharts | React-native charting, responsive |
| State | Zustand | Minimal boilerplate, performant |
| Styling | Tailwind CSS | Utility-first, rapid prototyping |
| PDF | jsPDF | Client-side report generation |
| BLE | Web Bluetooth API | Direct browser-to-device, no native app needed |

## FSR Sensor Placement

```
          BIG TOE
           (7)
    1st     3rd     5th
   META    META    META
    (4)     (5)     (6)

         MIDFOOT
          ARCH
           (3)


    HEEL    HEEL    HEEL
    MED    CENTER   LAT
    (1)     (0)     (2)
```

Positions based on clinical literature for plantar pressure analysis:
- **Heel (3 zones)**: Detect initial contact, heel strike force distribution
- **Midfoot arch**: Monitor arch collapse (pronation/supination)
- **Metatarsal heads (3 zones)**: Forefoot loading during push-off
- **Big toe**: Terminal stance and propulsion force

## Bilateral Operation

The system supports paired left/right insoles for asymmetry analysis:
- Each insole advertises as "SmartInsole-L" or "SmartInsole-R"
- App connects to both simultaneously
- Bilateral metrics: step time asymmetry, pressure loading asymmetry
- Asymmetry index is a strong predictor of fall risk
