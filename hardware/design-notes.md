# Smart Insole - Design Notes

## 1. MCU Selection: nRF52840 vs ESP32

| Parameter | nRF52840 | ESP32-S3 |
|---|---|---|
| BLE TX current | 4.6 mA (0 dBm) | 130 mA (BLE + WiFi radio) |
| BLE RX current | 4.6 mA | 95 mA |
| CPU sleep (RAM retained) | 1.5 uA | 8 uA |
| System OFF | 0.4 uA | 5 uA |
| ADC resolution | 12-bit (SAADC) | 12-bit (SAR) |
| ADC channels | 8 | 20 |
| Flash | 1 MB | 8 MB (external) |
| RAM | 256 KB | 512 KB |
| BLE version | 5.0 (2 Mbps PHY) | 5.0 |
| RTOS | Zephyr (nRF Connect SDK) | FreeRTOS (ESP-IDF) |

**Decision: nRF52840**. The 25x lower BLE current is the decisive factor. On a 150mAh battery, the nRF52840 runs for ~10 hours of continuous BLE streaming vs. <1.5 hours on ESP32. For a wearable that must operate all day, this is non-negotiable.

## 2. IMU Selection: BMI270 vs Alternatives

| Parameter | BMI270 | MPU-6050 | ICM-42688-P |
|---|---|---|---|
| Supply current (accel+gyro) | 685 uA | 3.9 mA | 970 uA |
| Accel noise density | 160 ug/rtHz | 400 ug/rtHz | 70 ug/rtHz |
| Gyro noise density | 0.014 dps/rtHz | 0.005 dps/rtHz | 0.0028 dps/rtHz |
| Built-in step counter | Yes | No | Yes |
| Wearable optimized | Yes | No | No |
| Package | LGA-14 2.5x3mm | QFN-24 4x4mm | LGA-14 2.5x3mm |
| Status | Active | NRND (obsolete) | Active |

**Decision: BMI270**. Lowest power consumption of any 6-axis IMU. Built-in step counter reduces MCU processing load. Noise performance is adequate for gait analysis (we filter to <25Hz anyway). The ICM-42688-P has better noise specs but draws 40% more power.

## 3. Power Budget Analysis

### Active Mode (BLE streaming at 20Hz)

| Component | Current | Duty Cycle | Average |
|---|---|---|---|
| nRF52840 CPU (64MHz) | 3.7 mA | 20% | 0.74 mA |
| nRF52840 BLE TX | 4.6 mA | 5% | 0.23 mA |
| nRF52840 BLE RX | 4.6 mA | 5% | 0.23 mA |
| nRF52840 ADC (SAADC) | 0.7 mA | 10% | 0.07 mA |
| nRF52840 SPI | 0.3 mA | 5% | 0.015 mA |
| BMI270 (accel+gyro 100Hz) | 0.685 mA | 100% | 0.685 mA |
| TMP117 (one-shot mode) | 0.25 mA | 0.1% | 0.00025 mA |
| CD74HC4051 (quiescent) | 0.001 mA | 100% | 0.001 mA |
| TPS62740 (quiescent) | 0.00036 mA | 100% | 0.00036 mA |
| FSR voltage dividers (8x) | 0.33 mA | 100% | 0.33 mA |
| **Total active** | | | **~2.3 mA** |

**Battery life (active)**: 150 mAh / 2.3 mA = **~65 hours** (theoretical)

Accounting for BLE connection overhead, voltage regulator efficiency (90%), and margin:
**Realistic estimate: 40-50 hours continuous operation**.

This exceeds the 8-12 hour target by a wide margin.

### Sleep Mode (no BLE, IMU motion detect)

| Component | Current |
|---|---|
| nRF52840 System ON idle | 1.5 uA |
| BMI270 low-power accel | 3.5 uA |
| TPS62740 quiescent | 0.36 uA |
| Leakage | ~1 uA |
| **Total sleep** | **~6.4 uA** |

**Battery life (sleep)**: 150 mAh / 0.0064 mA = **~23,400 hours (~2.7 years)**

## 4. FSR Placement Rationale

The 8 FSR positions are based on clinical plantar pressure analysis literature:

1. **Heel center**: Primary initial contact point during gait. Peak pressures during heel strike.
2. **Heel medial/lateral**: Detect pronation/supination during heel contact phase. Medial loading suggests overpronation (common in elderly).
3. **Midfoot arch**: Low pressure normally. Elevated pressure indicates flat foot / arch collapse.
4. **1st metatarsal head**: Primary weight-bearing during push-off. Reduced loading here correlates with reduced propulsion strength.
5. **3rd metatarsal head**: Center of forefoot. Reference point for medial-lateral pressure distribution.
6. **5th metatarsal head**: Lateral forefoot loading. Excess loading suggests supination gait pattern.
7. **Big toe (hallux)**: Terminal stance propulsion. Reduced hallux pressure is associated with balance deficits and fall risk.

**Why 8 sensors (not 16)?**

Research by Razak et al. (2012) and Saito et al. (2011) demonstrated that 6-8 sensors at key anatomical locations capture 95% of the variance in plantar pressure distribution compared to high-density sensor arrays (>200 sensors). Additional sensors add cost, wiring complexity, and power consumption without meaningful clinical benefit for fall risk assessment.

## 5. Antenna Considerations

- **Chip antenna** (Johanson 2450AT18x100) chosen over PCB trace antenna for its smaller footprint and consistent performance.
- **Ground plane**: Requires minimum 10x10mm ground plane beneath the antenna for proper operation. Our 25x18mm rigid PCB provides adequate ground.
- **Matching network**: PI-filter topology per Nordic Semiconductor's reference design (nRF52840-QIAA). Values (2.2pF, 3.9nH, 1.5pF) tuned for 2.4GHz ISM band.
- **Body effects**: Human body proximity detunes the antenna. In-shoe placement provides ~5mm of insole material between antenna and foot, which is sufficient separation. Expected range: 5-10 meters through shoe material.
- **Orientation**: Antenna oriented horizontally (parallel to ground) with ground plane below. Radiation pattern is primarily upward through the shoe.

## 6. EMC/EMI Considerations

- All power rails filtered with 100nF + 10uF ceramic capacitors
- SPI clock (up to 10MHz) routed on inner layers where possible, with ground return vias
- BLE radio section isolated on PCB corner with ground stitching vias
- USB-C connector protected with PRTR5V0U2X ESD clamp
- 32MHz crystal traces as short as possible (<5mm) with guard ground ring
- No split ground planes (single solid ground on L2)

## 7. Encapsulation and Waterproofing

### Silicone Potting (Rigid PCB)
- **Material**: Dow DOWSIL 3-4207 (medical-grade, shore A 40)
- **Process**: Dispense into TPU shell, cure at room temperature 24h
- **Protection level**: IP67 (1m submersion for 30 min)
- **USB-C access**: Silicone plug cap covers USB-C when not charging

### Flex PCB Lamination
- **Material**: Medical-grade silicone sheet (shore A 30)
- **Process**: Adhesive lamination (3M 468MP transfer tape) between two silicone layers
- **FSR windows**: Thinner silicone (0.3mm) over FSR pads to maintain pressure sensitivity
- **Edge seal**: Continuous silicone bond around perimeter

### Environmental Requirements
- Operating temperature: 10C to 45C (inside shoe)
- Humidity: up to 95% RH (foot sweat environment)
- Mechanical: withstand 100kg bodyweight repeatedly
- Washability: surface wipe clean, not machine washable

## 8. Bilateral Operation

The system supports paired insoles (left and right foot):

- **Identification**: Each insole programmed with "SmartInsole-L" or "SmartInsole-R" BLE device name. A solder jumper on the rigid PCB selects L/R configuration.
- **FSR mirroring**: Left foot FSR positions mirror right foot. "Heel medial" on left foot is the inner (right) side, "Heel medial" on right foot is the inner (left) side.
- **Synchronization**: Both insoles connect independently to the app. Timestamp synchronization uses BLE connection event counters for <1ms alignment.
- **Bilateral metrics**: Step time asymmetry = |step_time_L - step_time_R| / avg(step_time). Pressure asymmetry = |total_force_L - total_force_R| / avg(total_force).

## 9. Regulatory Considerations

### FDA Classification
If commercialized, this device would likely be classified as:
- **Class II medical device** (510(k) pathway)
- **Product code**: QMT (gait analysis system)
- **Predicate devices**: GAITRite, Tekscan F-Scan

### Standards
- **IEC 60601-1**: General safety (electrical, mechanical, thermal)
- **IEC 60601-1-2**: EMC requirements for medical devices
- **IEC 62304**: Software lifecycle for medical device software
- **ISO 14708**: Requirements for implantable and wearable devices
- **GDPR/HIPAA**: Patient gait data is PHI (Protected Health Information)

### Biocompatibility
- All skin-contact materials (silicone encapsulation) should meet **ISO 10993** biocompatibility testing
- No latex, no BPA, no phthalates in any patient-contact material

## 10. Testing and Validation Plan

### Hardware Validation
1. **Power**: Verify current draw matches power budget (<3mA active, <10uA sleep)
2. **Battery life**: Continuous BLE streaming test, target >24 hours
3. **ADC accuracy**: Calibrate FSR readings against known weights (0-100N range)
4. **IMU accuracy**: Compare BMI270 output against reference IMU (VICON motion capture)
5. **BLE range**: Verify >5m range through shoe material
6. **Waterproofing**: IP67 submersion test (1m, 30 min)
7. **Mechanical**: 1 million step-cycle fatigue test on flex PCB

### Software Validation
1. **Gait features**: Compare extracted features against gold-standard gait lab measurements
2. **ML model**: Validate XGBoost predictions against clinician assessments (target AUC >0.80)
3. **App**: Usability testing with 5+ elderly users and 3+ clinicians
4. **BLE reliability**: 24-hour continuous connection test, measure packet loss rate (target <0.1%)
