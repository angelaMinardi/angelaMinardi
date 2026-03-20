/*
 * Smart Insole - Digital Signal Processing Filters
 */

#ifndef SMART_INSOLE_FILTERS_H
#define SMART_INSOLE_FILTERS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * 2nd-order Butterworth IIR Filter
 * -------------------------------------------------------------------------*/

/**
 * State for a 2nd-order IIR (biquad) filter.
 * Stores the two previous input and output samples.
 */
struct butterworth_state {
    float x[2]; /* x[0] = x[n-1], x[1] = x[n-2] */
    float y[2]; /* y[0] = y[n-1], y[1] = y[n-2] */
};

/**
 * Zero-initialise the filter state.
 */
void butterworth_init(struct butterworth_state *state);

/**
 * Apply a 2nd-order IIR filter to one input sample.
 *
 * Transfer function (Direct Form I):
 *   y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
 *
 * @param state   Filter state (updated in place).
 * @param input   Current input sample x[n].
 * @param coeffs  Array of 5 coefficients: {b0, b1, b2, a1, a2}.
 * @return Filtered output y[n].
 */
float butterworth_apply(struct butterworth_state *state,
                        float input,
                        const float coeffs[5]);

/*
 * Pre-computed Butterworth low-pass coefficients.
 *
 * FSR_LP_COEFFS:  2nd-order, fc = 20 Hz, fs = 50 Hz
 *   Normalised freq = 20/50 = 0.4  (Wn = 0.8 in Nyquist units)
 *   Designed with bilinear transform.
 *
 * IMU_LP_COEFFS:  2nd-order, fc = 50 Hz, fs = 100 Hz  (Wn = 1.0 -> degenerate,
 *                 so we use fc = 45 Hz to stay practical)
 */
extern const float FSR_LP_COEFFS[5];
extern const float IMU_LP_COEFFS[5];

/* ---------------------------------------------------------------------------
 * Moving Average Filter
 * -------------------------------------------------------------------------*/

#define MOVING_AVG_WINDOW  5

/**
 * State for a simple moving-average filter.
 */
struct moving_avg_state {
    float buffer[MOVING_AVG_WINDOW];
    uint8_t index;
    uint8_t count;
    float   sum;
};

/**
 * Zero-initialise the moving-average filter state.
 */
void moving_avg_init(struct moving_avg_state *state);

/**
 * Apply the moving-average filter to one input sample.
 *
 * @param state  Filter state (updated in place).
 * @param input  Current input sample.
 * @return Moving average output.
 */
float moving_avg_apply(struct moving_avg_state *state, float input);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_FILTERS_H */
