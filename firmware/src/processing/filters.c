/*
 * Smart Insole - Digital Signal Processing Filters
 *
 * Implements 2nd-order Butterworth IIR (biquad) and simple moving-average
 * filters for FSR and IMU signal conditioning.
 */

#include "filters.h"
#include <string.h>

/* ---------------------------------------------------------------------------
 * Pre-computed Butterworth low-pass coefficients
 *
 * Designed using the bilinear transform:
 *   s-domain 2nd-order Butterworth: H(s) = 1 / (s^2 + sqrt(2)*s + 1)
 *   Pre-warped cutoff: Omega = tan(pi * fc / fs)
 *
 * FSR: fc = 20 Hz, fs = 50 Hz
 *   Omega = tan(pi * 20 / 50) = tan(0.4 * pi) = 3.07768
 *   K = Omega^2 = 9.47194
 *   denom = 1 + sqrt(2)*Omega + K = 1 + 4.35117 + 9.47194 = 14.82311
 *   b0 = K / denom = 0.63913
 *   b1 = 2 * K / denom = 1.27826
 *   b2 = K / denom = 0.63913
 *   a1 = 2 * (K - 1) / denom = 1.14298
 *   a2 = (1 - sqrt(2)*Omega + K) / denom = 0.41254
 *
 * IMU: fc = 45 Hz, fs = 100 Hz  (using 45 Hz to avoid degenerate case)
 *   Omega = tan(pi * 45 / 100) = tan(0.45 * pi) = 6.31375
 *   K = Omega^2 = 39.86344
 *   denom = 1 + sqrt(2)*Omega + K = 1 + 8.92955 + 39.86344 = 49.79299
 *   b0 = K / denom = 0.80052
 *   b1 = 2 * K / denom = 1.60105
 *   b2 = K / denom = 0.80052
 *   a1 = 2 * (K - 1) / denom = 1.56102
 *   a2 = (1 - sqrt(2)*Omega + K) / denom = 0.64158
 * -------------------------------------------------------------------------*/

const float FSR_LP_COEFFS[5] = {
    /* b0,       b1,       b2,       a1,       a2 */
    0.63913f, 1.27826f, 0.63913f, 1.14298f, 0.41254f
};

const float IMU_LP_COEFFS[5] = {
    0.80052f, 1.60105f, 0.80052f, 1.56102f, 0.64158f
};

/* ---------------------------------------------------------------------------
 * Butterworth IIR Filter
 * -------------------------------------------------------------------------*/

void butterworth_init(struct butterworth_state *state)
{
    memset(state, 0, sizeof(*state));
}

float butterworth_apply(struct butterworth_state *state,
                        float input,
                        const float coeffs[5])
{
    float b0 = coeffs[0];
    float b1 = coeffs[1];
    float b2 = coeffs[2];
    float a1 = coeffs[3];
    float a2 = coeffs[4];

    /* Direct Form I:
     *   y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
     */
    float output = b0 * input
                 + b1 * state->x[0]
                 + b2 * state->x[1]
                 - a1 * state->y[0]
                 - a2 * state->y[1];

    /* Shift delay line */
    state->x[1] = state->x[0];
    state->x[0] = input;
    state->y[1] = state->y[0];
    state->y[0] = output;

    return output;
}

/* ---------------------------------------------------------------------------
 * Moving Average Filter
 * -------------------------------------------------------------------------*/

void moving_avg_init(struct moving_avg_state *state)
{
    memset(state, 0, sizeof(*state));
}

float moving_avg_apply(struct moving_avg_state *state, float input)
{
    /* If the buffer is full, subtract the oldest value */
    if (state->count >= MOVING_AVG_WINDOW) {
        state->sum -= state->buffer[state->index];
    } else {
        state->count++;
    }

    /* Insert new value */
    state->buffer[state->index] = input;
    state->sum += input;

    /* Advance circular index */
    state->index++;
    if (state->index >= MOVING_AVG_WINDOW) {
        state->index = 0;
    }

    return state->sum / (float)state->count;
}
