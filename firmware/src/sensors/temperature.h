/*
 * Smart Insole - TMP117 Temperature Sensor Driver (I2C)
 */

#ifndef SMART_INSOLE_TEMPERATURE_H
#define SMART_INSOLE_TEMPERATURE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialise the TMP117 temperature sensor over I2C.
 * Configures one-shot measurement mode for low power consumption.
 *
 * @return 0 on success, negative errno on failure.
 */
int temperature_init(void);

/**
 * Trigger a one-shot measurement and read the temperature.
 *
 * @return Temperature in 0.01 degree Celsius units (e.g. 2950 = 29.50 C).
 *         Returns INT16_MIN on read failure.
 */
int16_t temperature_read(void);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_TEMPERATURE_H */
