/*
 * Smart Insole - Power Management
 */

#ifndef SMART_INSOLE_POWER_MANAGER_H
#define SMART_INSOLE_POWER_MANAGER_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialise the power management subsystem.
 * Configures battery voltage ADC channel.
 *
 * @return 0 on success, negative errno on failure.
 */
int power_manager_init(void);

/**
 * Read battery percentage (0-100%).
 * Uses a voltage divider (2x 100k resistors) and maps the LiPo
 * discharge curve to a percentage.
 *
 * @return Battery percentage (0-100). Updates cached value.
 */
uint8_t power_get_battery_pct(void);

/**
 * Check if the device has been idle (no IMU motion) for 5+ minutes.
 * If so, enter deep sleep with IMU motion wakeup interrupt.
 */
void power_check_idle(void);

/**
 * Enter shipping mode (ultra-deep sleep for long-term storage).
 * Only wakes on reset or specific hardware trigger.
 */
void power_enter_shipping_mode(void);

/**
 * Report the latest motion timestamp (called by IMU / sensor manager
 * whenever significant motion is detected).
 */
void power_report_motion(void);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_POWER_MANAGER_H */
