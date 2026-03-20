/*
 * Smart Insole - BMI270 IMU Driver (SPI)
 */

#ifndef SMART_INSOLE_IMU_H
#define SMART_INSOLE_IMU_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Raw IMU data from accelerometer and gyroscope.
 */
struct imu_data {
    int16_t accel_x;
    int16_t accel_y;
    int16_t accel_z;
    int16_t gyro_x;
    int16_t gyro_y;
    int16_t gyro_z;
};

/**
 * Initialise the BMI270 IMU over SPI.
 * Performs soft reset, chip-ID verification, config upload,
 * and accelerometer / gyroscope configuration.
 *
 * @return 0 on success, negative errno on failure.
 */
int imu_init(void);

/**
 * Burst-read accelerometer and gyroscope data.
 *
 * @param data  Output structure filled with raw sensor values.
 * @return 0 on success, negative errno on failure.
 */
int imu_read(struct imu_data *data);

/**
 * Read the hardware step counter value.
 *
 * @return Current step count (wraps at 65535).
 */
uint16_t imu_get_step_count(void);

/**
 * Check whether the most recent data-ready interrupt has fired.
 */
bool imu_data_ready(void);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_IMU_H */
