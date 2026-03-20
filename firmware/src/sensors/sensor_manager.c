/*
 * Smart Insole - Sensor Manager Implementation
 */

#include "sensor_manager.h"
#include "fsr.h"
#include "imu.h"
#include "temperature.h"
#include "power/power_manager.h"
#include "processing/gait_features.h"

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <string.h>

LOG_MODULE_REGISTER(sensor_manager, CONFIG_LOG_DEFAULT_LEVEL);

/* ---------------------------------------------------------------------------
 * Message queue for BLE thread
 * -------------------------------------------------------------------------*/
#define PACKET_QUEUE_DEPTH  8

K_MSGQ_DEFINE(gait_packet_queue, sizeof(struct gait_data_packet),
              PACKET_QUEUE_DEPTH, 4);

/* ---------------------------------------------------------------------------
 * Internal state
 * -------------------------------------------------------------------------*/
static uint32_t sample_counter;     /* Counts every 100 Hz call */
static uint16_t packet_id_counter;  /* Monotonic packet ID for BLE */

/* Latest sensor values (updated at their respective rates) */
static uint16_t         latest_fsr[FSR_CHANNEL_COUNT];
static struct imu_data  latest_imu;
static int16_t          latest_temperature; /* 0.01 C units */

/* ---------------------------------------------------------------------------
 * CRC-16 / CCITT (polynomial 0x1021, init 0xFFFF)
 * -------------------------------------------------------------------------*/
uint16_t crc16_compute(const uint8_t *data, uint16_t len)
{
    uint16_t crc = 0xFFFF;

    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

/* ---------------------------------------------------------------------------
 * Public API
 * -------------------------------------------------------------------------*/

int sensor_manager_init(void)
{
    int ret;

    sample_counter   = 0;
    packet_id_counter = 0;
    memset(latest_fsr, 0, sizeof(latest_fsr));
    memset(&latest_imu, 0, sizeof(latest_imu));
    latest_temperature = 0;

    ret = fsr_init();
    if (ret < 0) {
        LOG_ERR("FSR init failed: %d", ret);
        return ret;
    }

    ret = imu_init();
    if (ret < 0) {
        LOG_ERR("IMU init failed: %d", ret);
        return ret;
    }

    ret = temperature_init();
    if (ret < 0) {
        LOG_ERR("Temperature sensor init failed: %d", ret);
        return ret;
    }

    gait_features_init();

    LOG_INF("Sensor manager initialised");
    return 0;
}

void sensor_manager_sample(void)
{
    /* ---- IMU: every call (100 Hz) ---- */
    int ret = imu_read(&latest_imu);
    if (ret < 0) {
        LOG_DBG("IMU read failed: %d", ret);
    }

    /* ---- FSR: every 2nd call (50 Hz) ---- */
    if ((sample_counter % 2) == 0) {
        ret = fsr_read_all(latest_fsr);
        if (ret < 0) {
            LOG_DBG("FSR read failed: %d", ret);
        }
    }

    /* ---- Temperature: every 1000th call (~0.1 Hz, every 10 s) ---- */
    if ((sample_counter % 1000) == 0) {
        latest_temperature = temperature_read();
    }

    /* ---- Build and enqueue packet every 5th call (20 Hz) ---- */
    if ((sample_counter % 5) == 0) {
        struct gait_data_packet pkt;
        memset(&pkt, 0, sizeof(pkt));

        pkt.packet_id    = packet_id_counter++;
        pkt.timestamp_ms = k_uptime_get_32();

        memcpy(pkt.fsr, latest_fsr, sizeof(pkt.fsr));

        pkt.accel[0] = latest_imu.accel_x;
        pkt.accel[1] = latest_imu.accel_y;
        pkt.accel[2] = latest_imu.accel_z;
        pkt.gyro[0]  = latest_imu.gyro_x;
        pkt.gyro[1]  = latest_imu.gyro_y;
        pkt.gyro[2]  = latest_imu.gyro_z;

        pkt.step_count   = imu_get_step_count();
        pkt.battery_pct  = power_get_battery_pct();
        pkt.status_flags = 0x00;

        /* Set low-battery flag if below 15% */
        if (pkt.battery_pct < 15) {
            pkt.status_flags |= 0x02;
        }

        /* CRC over first 38 bytes (everything except the CRC field itself) */
        pkt.crc16 = crc16_compute((const uint8_t *)&pkt,
                                   sizeof(pkt) - sizeof(pkt.crc16));

        /* Update on-device gait metrics (non-blocking) */
        update_gait_metrics(get_gait_metrics_ptr(), &pkt);

        /* Enqueue for BLE thread; drop oldest if full */
        ret = k_msgq_put(&gait_packet_queue, &pkt, K_NO_WAIT);
        if (ret == -ENOMSG || ret == -EAGAIN) {
            /* Queue full - purge oldest and try again */
            struct gait_data_packet discard;
            k_msgq_get(&gait_packet_queue, &discard, K_NO_WAIT);
            k_msgq_put(&gait_packet_queue, &pkt, K_NO_WAIT);
        }
    }

    sample_counter++;
}

int sensor_manager_get_packet(struct gait_data_packet *pkt)
{
    return k_msgq_get(&gait_packet_queue, pkt, K_FOREVER);
}
