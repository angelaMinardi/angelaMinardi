/*
 * Smart Insole - On-Device Gait Feature Extraction
 *
 * Computes real-time gait metrics from FSR and IMU data:
 *   - Cadence (steps/min) from heel-strike intervals
 *   - Stance percentage from heel-strike to toe-off timing
 *   - Centre of pressure (AP + ML) from weighted FSR values
 *   - Lateral sway RMS from medial-lateral accelerometer axis
 */

#include "gait_features.h"
#include "filters.h"

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <math.h>
#include <string.h>

LOG_MODULE_REGISTER(gait_features, CONFIG_LOG_DEFAULT_LEVEL);

/* ---------------------------------------------------------------------------
 * Thresholds and constants
 * -------------------------------------------------------------------------*/
#define HEEL_STRIKE_THRESHOLD   500    /* ADC counts (~1.2 N) */
#define TOE_OFF_THRESHOLD       300    /* ADC counts (~0.7 N) */

/* Minimum interval between heel strikes to reject noise (200 ms = 300 spm max) */
#define MIN_STRIDE_MS           200
/* Maximum interval before resetting cadence (3000 ms = 20 spm min) */
#define MAX_STRIDE_MS           3000

/* Accelerometer scaling: +/-8g range, 16-bit signed => 1 LSB = 8/32768 g */
#define ACCEL_SCALE_G           (8.0f / 32768.0f)
#define G_TO_MS2                9.80665f

/* RMS smoothing: exponential moving average alpha */
#define SWAY_RMS_ALPHA          0.05f

/*
 * FSR zone positions for COP calculation.
 * Normalised coordinates: AP 0.0 (heel) .. 1.0 (toe),
 *                         ML 0.0 (lateral) .. 1.0 (medial).
 *
 * Indices correspond to fsr_zone enum in fsr.h:
 *   0: HEEL_CENTER,  1: HEEL_MEDIAL,   2: HEEL_LATERAL,  3: MIDFOOT_ARCH,
 *   4: META_1ST,     5: META_3RD,      6: META_5TH,      7: BIG_TOE
 */
static const float fsr_pos_ap[8] = {
    0.10f, 0.12f, 0.08f, 0.40f, 0.70f, 0.75f, 0.78f, 0.95f
};
static const float fsr_pos_ml[8] = {
    0.50f, 0.75f, 0.25f, 0.70f, 0.80f, 0.50f, 0.20f, 0.85f
};

/* ---------------------------------------------------------------------------
 * Internal state
 * -------------------------------------------------------------------------*/
static struct gait_metrics current_metrics;

/* Heel-strike detection state */
static bool     heel_was_below;       /* Previous sample below threshold */
static uint32_t last_heel_strike_ms;  /* Timestamp of last heel strike */
static uint32_t prev_heel_strike_ms;  /* Timestamp of the one before that */

/* Toe-off detection state */
static bool     toe_was_above;        /* Previous sample above threshold */
static uint32_t last_toe_off_ms;

/* Sway RMS accumulator */
static float sway_rms_accum;
static uint32_t sway_sample_count;

/* Butterworth filter for medial-lateral accelerometer */
static struct butterworth_state ml_accel_filter;

/* ---------------------------------------------------------------------------
 * Public API
 * -------------------------------------------------------------------------*/

void gait_features_init(void)
{
    memset(&current_metrics, 0, sizeof(current_metrics));
    current_metrics.symmetry_index = 1.0f; /* default: perfect symmetry */

    heel_was_below      = true;
    last_heel_strike_ms = 0;
    prev_heel_strike_ms = 0;

    toe_was_above       = false;
    last_toe_off_ms     = 0;

    sway_rms_accum    = 0.0f;
    sway_sample_count = 0;

    butterworth_init(&ml_accel_filter);
}

bool detect_heel_strike(uint16_t fsr_heel, uint16_t threshold)
{
    bool currently_above = (fsr_heel >= threshold);
    bool strike = false;

    /* Rising edge: was below threshold, now above */
    if (heel_was_below && currently_above) {
        uint32_t now = k_uptime_get_32();
        uint32_t interval = now - last_heel_strike_ms;

        if (interval >= MIN_STRIDE_MS) {
            strike = true;
            prev_heel_strike_ms = last_heel_strike_ms;
            last_heel_strike_ms = now;
        }
    }

    heel_was_below = !currently_above;
    return strike;
}

bool detect_toe_off(uint16_t fsr_toe, uint16_t threshold)
{
    bool currently_below = (fsr_toe < threshold);
    bool toe_off = false;

    /* Falling edge: was above threshold, now below */
    if (toe_was_above && currently_below) {
        last_toe_off_ms = k_uptime_get_32();
        toe_off = true;
    }

    toe_was_above = !currently_below;
    return toe_off;
}

void update_gait_metrics(struct gait_metrics *m,
                         struct gait_data_packet *pkt)
{
    uint32_t now = pkt->timestamp_ms;

    /* ---- Heel strike & cadence ---- */
    /* Use HEEL_CENTER (index 0) for strike detection */
    bool strike = detect_heel_strike(pkt->fsr[0], HEEL_STRIKE_THRESHOLD);
    if (strike && prev_heel_strike_ms > 0) {
        uint32_t stride_ms = last_heel_strike_ms - prev_heel_strike_ms;
        if (stride_ms > 0 && stride_ms <= MAX_STRIDE_MS) {
            /* cadence = 60000 / stride_ms (steps/min for single foot,
             * multiply by 2 for total step rate if needed) */
            float new_cadence = 60000.0f / (float)stride_ms;
            /* Exponential smoothing */
            m->cadence = m->cadence * 0.7f + new_cadence * 0.3f;
        }
    }

    /* Decay cadence if no strike for a long time */
    if ((now - last_heel_strike_ms) > MAX_STRIDE_MS && last_heel_strike_ms > 0) {
        m->cadence *= 0.95f;
        if (m->cadence < 1.0f) {
            m->cadence = 0.0f;
        }
    }

    /* ---- Toe-off & stance percentage ---- */
    detect_toe_off(pkt->fsr[7], TOE_OFF_THRESHOLD);

    if (last_heel_strike_ms > 0 && last_toe_off_ms > last_heel_strike_ms) {
        uint32_t stance_ms = last_toe_off_ms - last_heel_strike_ms;
        uint32_t stride_ms = last_heel_strike_ms - prev_heel_strike_ms;
        if (stride_ms > 0) {
            float stance_frac = (float)stance_ms / (float)stride_ms;
            if (stance_frac > 1.0f) { stance_frac = 1.0f; }
            m->stance_pct = m->stance_pct * 0.7f + (stance_frac * 100.0f) * 0.3f;
        }
    }

    /* ---- Centre of Pressure (COP) from 8 FSR values ---- */
    float total_force = 0.0f;
    float cop_ap_weighted = 0.0f;
    float cop_ml_weighted = 0.0f;

    for (int i = 0; i < 8; i++) {
        float f = (float)pkt->fsr[i];
        total_force     += f;
        cop_ap_weighted += f * fsr_pos_ap[i];
        cop_ml_weighted += f * fsr_pos_ml[i];
    }

    if (total_force > 10.0f) { /* Minimum force to compute meaningful COP */
        float cop_ap = cop_ap_weighted / total_force;
        float cop_ml = cop_ml_weighted / total_force;
        /* Smooth */
        m->cop_ap = m->cop_ap * 0.8f + cop_ap * 0.2f;
        m->cop_ml = m->cop_ml * 0.8f + cop_ml * 0.2f;
    }

    /* ---- Lateral sway from IMU ---- */
    /* Use accel_y as medial-lateral axis (assuming insole coordinate frame) */
    float ml_accel_g = (float)pkt->accel[1] * ACCEL_SCALE_G;
    float ml_accel_ms2 = ml_accel_g * G_TO_MS2;

    /* Filter the ML acceleration */
    float filtered_ml = butterworth_apply(&ml_accel_filter,
                                          ml_accel_ms2,
                                          IMU_LP_COEFFS);

    /* Incremental RMS using exponential moving average of squared values */
    float sq = filtered_ml * filtered_ml;
    sway_rms_accum = sway_rms_accum * (1.0f - SWAY_RMS_ALPHA) + sq * SWAY_RMS_ALPHA;
    sway_sample_count++;

    if (sway_sample_count > 10) {
        m->sway_rms = sqrtf(sway_rms_accum);
    }

    /* symmetry_index is a placeholder for dual-insole systems */
    m->symmetry_index = 1.0f;
}

const struct gait_metrics *get_gait_metrics(void)
{
    return &current_metrics;
}

struct gait_metrics *get_gait_metrics_ptr(void)
{
    return &current_metrics;
}
