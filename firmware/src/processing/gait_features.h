/*
 * Smart Insole - On-Device Gait Feature Extraction
 */

#ifndef SMART_INSOLE_GAIT_FEATURES_H
#define SMART_INSOLE_GAIT_FEATURES_H

#include <stdint.h>
#include <stdbool.h>
#include "sensors/sensor_manager.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Running gait metrics computed on-device.
 */
struct gait_metrics {
    float cadence;         /* Steps per minute                             */
    float stance_pct;      /* Percentage of gait cycle in stance phase     */
    float cop_ap;          /* Centre of pressure, anterior-posterior (0-1) */
    float cop_ml;          /* Centre of pressure, medial-lateral   (0-1)  */
    float sway_rms;        /* Lateral sway RMS from IMU (m/s^2)           */
    float symmetry_index;  /* L/R symmetry (1.0 = perfect, not used on    */
                           /* single insole; placeholder for dual-insole)  */
};

/**
 * Initialise gait analysis state.
 */
void gait_features_init(void);

/**
 * Detect a heel-strike event (rising-edge on heel FSR).
 *
 * @param fsr_heel    Current heel FSR ADC value.
 * @param threshold   ADC threshold for strike detection.
 * @return true if a heel strike is detected on this sample.
 */
bool detect_heel_strike(uint16_t fsr_heel, uint16_t threshold);

/**
 * Detect a toe-off event (falling-edge on toe FSR).
 *
 * @param fsr_toe     Current big-toe FSR ADC value.
 * @param threshold   ADC threshold for toe-off detection.
 * @return true if a toe-off is detected on this sample.
 */
bool detect_toe_off(uint16_t fsr_toe, uint16_t threshold);

/**
 * Update running gait metrics with a new data packet.
 * Call this at 20 Hz (once per BLE packet).
 *
 * @param m    Gait metrics structure to update in place.
 * @param pkt  Latest gait data packet.
 */
void update_gait_metrics(struct gait_metrics *m,
                         struct gait_data_packet *pkt);

/**
 * Get a const pointer to the current gait metrics.
 */
const struct gait_metrics *get_gait_metrics(void);

/**
 * Get a mutable pointer (for sensor_manager to update).
 */
struct gait_metrics *get_gait_metrics_ptr(void);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_GAIT_FEATURES_H */
