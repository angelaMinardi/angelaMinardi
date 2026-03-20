/*
 * Smart Insole - Sensor Manager
 *
 * Orchestrates all sensor reads at appropriate rates and packs data
 * into gait_data_packet structures for BLE transmission.
 */

#ifndef SMART_INSOLE_SENSOR_MANAGER_H
#define SMART_INSOLE_SENSOR_MANAGER_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Gait data packet - 40 bytes, matches BLE characteristic layout */
struct gait_data_packet {
    uint16_t packet_id;       /* Monotonically increasing packet counter     */
    uint32_t timestamp_ms;    /* System uptime in milliseconds               */
    uint16_t fsr[8];          /* 8 FSR ADC values (12-bit in 16-bit field)   */
    int16_t  accel[3];        /* Accelerometer X, Y, Z raw                   */
    int16_t  gyro[3];         /* Gyroscope X, Y, Z raw                       */
    uint16_t step_count;      /* Hardware step counter                       */
    uint8_t  battery_pct;     /* Battery percentage (0-100)                  */
    uint8_t  status_flags;    /* Bit flags: [0] charging, [1] low-batt, etc. */
    uint16_t crc16;           /* CRC-16/CCITT over preceding 38 bytes        */
} __attribute__((packed));

/* Verify the struct is exactly 40 bytes */
_Static_assert(sizeof(struct gait_data_packet) == 40,
               "gait_data_packet must be 40 bytes");

/**
 * Initialise all sensor subsystems (FSR, IMU, temperature).
 * @return 0 on success, negative errno on first failure.
 */
int sensor_manager_init(void);

/**
 * Execute one sensor sampling cycle.  Called at 100 Hz from sensor_thread.
 * - IMU is read every call (100 Hz).
 * - FSR is read every 2nd call (50 Hz).
 * - Temperature is read every 1000th call (~0.1 Hz).
 * Every 5th call a gait_data_packet is enqueued for BLE.
 */
void sensor_manager_sample(void);

/**
 * Dequeue the next gait_data_packet (blocking).
 * @param pkt  Output packet.
 * @return 0 on success, negative errno on failure / timeout.
 */
int sensor_manager_get_packet(struct gait_data_packet *pkt);

/**
 * Compute CRC-16/CCITT over a byte buffer.
 */
uint16_t crc16_compute(const uint8_t *data, uint16_t len);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_SENSOR_MANAGER_H */
