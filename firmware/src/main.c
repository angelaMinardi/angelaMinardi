/*
 * Smart Insole Fall Prevention System - Main Entry Point
 *
 * Initializes all subsystems and creates three worker threads:
 *   1. sensor_thread  (priority 7)  - 100Hz sensor sampling
 *   2. ble_thread     (priority 8)  - 20Hz BLE notification
 *   3. power_thread   (priority 10) - 1Hz battery & sleep management
 */

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/sys/reboot.h>

#include "sensors/sensor_manager.h"
#include "ble/ble_manager.h"
#include "ble/ble_service.h"
#include "power/power_manager.h"

LOG_MODULE_REGISTER(main, CONFIG_LOG_DEFAULT_LEVEL);

/* ---------------------------------------------------------------------------
 * Thread stack sizes & priorities
 * -------------------------------------------------------------------------*/
#define SENSOR_THREAD_STACK_SIZE  2048
#define BLE_THREAD_STACK_SIZE     2048
#define POWER_THREAD_STACK_SIZE   1024

#define SENSOR_THREAD_PRIORITY  7
#define BLE_THREAD_PRIORITY     8
#define POWER_THREAD_PRIORITY   10

K_THREAD_STACK_DEFINE(sensor_thread_stack, SENSOR_THREAD_STACK_SIZE);
K_THREAD_STACK_DEFINE(ble_thread_stack, BLE_THREAD_STACK_SIZE);
K_THREAD_STACK_DEFINE(power_thread_stack, POWER_THREAD_STACK_SIZE);

static struct k_thread sensor_thread_data;
static struct k_thread ble_thread_data;
static struct k_thread power_thread_data;

/* ---------------------------------------------------------------------------
 * Thread entry points
 * -------------------------------------------------------------------------*/

/**
 * Sensor thread - runs the sensor manager sampling loop at 100 Hz (10 ms).
 */
static void sensor_thread_entry(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    LOG_INF("Sensor thread started");

    while (1) {
        sensor_manager_sample();
        k_sleep(K_MSEC(10)); /* 100 Hz */
    }
}

/**
 * BLE thread - dequeues gait data packets and sends BLE notifications at ~20 Hz.
 */
static void ble_thread_entry(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    LOG_INF("BLE thread started");

    struct gait_data_packet pkt;

    while (1) {
        /* Block until a packet is available in the message queue */
        int ret = sensor_manager_get_packet(&pkt);

        if (ret == 0 && ble_is_connected()) {
            gait_service_notify(&pkt);
        }
        /* If not connected, discard the packet silently */
    }
}

/**
 * Power thread - monitors battery at 1 Hz and manages sleep.
 */
static void power_thread_entry(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    LOG_INF("Power thread started");

    while (1) {
        /* Update global battery percentage (consumed by sensor_manager) */
        power_get_battery_pct();

        /* Check if the device has been idle long enough to enter deep sleep */
        power_check_idle();

        k_sleep(K_MSEC(1000)); /* 1 Hz */
    }
}

/* ---------------------------------------------------------------------------
 * main
 * -------------------------------------------------------------------------*/
int main(void)
{
    int ret;

    LOG_INF("Smart Insole firmware starting...");

    /* ---- Initialize subsystems ---- */
    ret = sensor_manager_init();
    if (ret < 0) {
        LOG_ERR("Sensor manager init failed: %d", ret);
    }

    ret = power_manager_init();
    if (ret < 0) {
        LOG_ERR("Power manager init failed: %d", ret);
    }

    ret = ble_manager_init();
    if (ret < 0) {
        LOG_ERR("BLE manager init failed: %d", ret);
        /* Continue anyway; sensors can still log locally */
    }

    ret = gait_service_init();
    if (ret < 0) {
        LOG_ERR("GATT service init failed: %d", ret);
    }

    /* ---- Create worker threads ---- */
    k_thread_create(&sensor_thread_data,
                     sensor_thread_stack,
                     K_THREAD_STACK_SIZEOF(sensor_thread_stack),
                     sensor_thread_entry,
                     NULL, NULL, NULL,
                     SENSOR_THREAD_PRIORITY, 0, K_NO_WAIT);
    k_thread_name_set(&sensor_thread_data, "sensor_thread");

    k_thread_create(&ble_thread_data,
                     ble_thread_stack,
                     K_THREAD_STACK_SIZEOF(ble_thread_stack),
                     ble_thread_entry,
                     NULL, NULL, NULL,
                     BLE_THREAD_PRIORITY, 0, K_NO_WAIT);
    k_thread_name_set(&ble_thread_data, "ble_thread");

    k_thread_create(&power_thread_data,
                     power_thread_stack,
                     K_THREAD_STACK_SIZEOF(power_thread_stack),
                     power_thread_entry,
                     NULL, NULL, NULL,
                     POWER_THREAD_PRIORITY, 0, K_NO_WAIT);
    k_thread_name_set(&power_thread_data, "power_thread");

    /* ---- Start BLE advertising ---- */
    ret = ble_manager_start_advertising();
    if (ret < 0) {
        LOG_ERR("Advertising start failed: %d", ret);
    } else {
        LOG_INF("BLE advertising started");
    }

    LOG_INF("Smart Insole firmware initialised – entering idle");

    /* Main thread has nothing left to do; let scheduler run workers. */
    return 0;
}
