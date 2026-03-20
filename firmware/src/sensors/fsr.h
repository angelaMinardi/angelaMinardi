/*
 * Smart Insole - FSR Array Driver (CD74HC4051 MUX + ADC)
 */

#ifndef SMART_INSOLE_FSR_H
#define SMART_INSOLE_FSR_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Number of FSR channels via the 8:1 MUX */
#define FSR_CHANNEL_COUNT  8

/* FSR zone mapping to MUX channel index */
enum fsr_zone {
    FSR_HEEL_CENTER   = 0,
    FSR_HEEL_MEDIAL   = 1,
    FSR_HEEL_LATERAL  = 2,
    FSR_MIDFOOT_ARCH  = 3,
    FSR_META_1ST      = 4,
    FSR_META_3RD      = 5,
    FSR_META_5TH      = 6,
    FSR_BIG_TOE       = 7,
};

/**
 * Initialise the ADC channel and MUX select GPIO pins.
 * @return 0 on success, negative errno on failure.
 */
int fsr_init(void);

/**
 * Read all 8 MUX channels sequentially.
 * @param values  Output array of 12-bit ADC values (0-4095), one per channel.
 * @return 0 on success, negative errno on failure.
 */
int fsr_read_all(uint16_t values[FSR_CHANNEL_COUNT]);

/**
 * Convert a raw ADC value to force in Newtons using the FSR 402 characteristic.
 * @param adc_value  12-bit ADC reading.
 * @return Force in Newtons (0.0 if no force detected).
 */
float fsr_to_force(uint16_t adc_value);

/**
 * Return a human-readable name for a zone index.
 */
const char *fsr_zone_name(enum fsr_zone zone);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_FSR_H */
