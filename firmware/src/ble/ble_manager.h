/*
 * Smart Insole - BLE Connection Manager
 */

#ifndef SMART_INSOLE_BLE_MANAGER_H
#define SMART_INSOLE_BLE_MANAGER_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialise the BLE subsystem and register connection callbacks.
 * @return 0 on success, negative errno on failure.
 */
int ble_manager_init(void);

/**
 * Start connectable BLE advertising with device name.
 * @return 0 on success, negative errno on failure.
 */
int ble_manager_start_advertising(void);

/**
 * Stop BLE advertising.
 * @return 0 on success, negative errno on failure.
 */
int ble_manager_stop_advertising(void);

/**
 * Query whether a central device is currently connected.
 */
bool ble_is_connected(void);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_BLE_MANAGER_H */
