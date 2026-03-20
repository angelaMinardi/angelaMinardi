/*
 * Smart Insole - Custom BLE GATT Service
 */

#ifndef SMART_INSOLE_BLE_SERVICE_H
#define SMART_INSOLE_BLE_SERVICE_H

#include <stdint.h>
#include "sensors/sensor_manager.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialise the custom GATT service and register it with the BLE stack.
 * @return 0 on success, negative errno on failure.
 */
int gait_service_init(void);

/**
 * Send a gait data packet as a BLE notification (if a client is subscribed).
 * @param pkt  Pointer to the 40-byte gait data packet.
 * @return 0 on success, negative errno on failure or if not subscribed.
 */
int gait_service_notify(struct gait_data_packet *pkt);

#ifdef __cplusplus
}
#endif

#endif /* SMART_INSOLE_BLE_SERVICE_H */
