/*
 * Smart Insole - Custom BLE GATT Service
 *
 * Defines a custom service with three characteristics:
 *   1. GAIT_DATA  (notify)     - 40-byte gait data packets
 *   2. CONFIG     (read/write) - sampling configuration
 *   3. DEVICE_INFO (read)      - firmware version and serial number
 *
 * Base UUID: 12345678-1234-5678-1234-56789abcdef0
 */

#include "ble_service.h"

#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/logging/log.h>
#include <string.h>

LOG_MODULE_REGISTER(ble_service, CONFIG_LOG_DEFAULT_LEVEL);

/* ---------------------------------------------------------------------------
 * UUIDs
 * -------------------------------------------------------------------------*/

/* Service UUID: 12345678-1234-5678-1234-56789abcdef0 */
static struct bt_uuid_128 gait_service_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x5678, 0x1234, 0x56789abcdef0));

/* Gait Data characteristic UUID: ...def1 */
static struct bt_uuid_128 gait_data_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x5678, 0x1234, 0x56789abcdef1));

/* Config characteristic UUID: ...def2 */
static struct bt_uuid_128 config_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x5678, 0x1234, 0x56789abcdef2));

/* Device Info characteristic UUID: ...def3 */
static struct bt_uuid_128 device_info_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x5678, 0x1234, 0x56789abcdef3));

/* ---------------------------------------------------------------------------
 * Characteristic data
 * -------------------------------------------------------------------------*/

/* Config characteristic value: sampling rate config (default 100 Hz IMU, 50 Hz FSR) */
struct sampling_config {
    uint8_t imu_rate_hz;   /* IMU sampling rate (default 100) */
    uint8_t fsr_rate_hz;   /* FSR sampling rate (default 50)  */
    uint8_t notify_rate_hz;/* BLE notification rate (default 20) */
    uint8_t reserved;
} __attribute__((packed));

static struct sampling_config current_config = {
    .imu_rate_hz    = 100,
    .fsr_rate_hz    = 50,
    .notify_rate_hz = 20,
    .reserved       = 0,
};

/* Device info: firmware version + serial */
#define FW_VERSION  "1.0.0"
#define SERIAL_NUM  "SI-00001"

struct device_info_data {
    char fw_version[8];
    char serial[12];
} __attribute__((packed));

static struct device_info_data dev_info = {
    .fw_version = FW_VERSION,
    .serial     = SERIAL_NUM,
};

/* Notification enabled flag */
static bool gait_data_notify_enabled;

/* ---------------------------------------------------------------------------
 * CCC (Client Characteristic Configuration) changed callback
 * -------------------------------------------------------------------------*/
static void gait_data_ccc_changed(const struct bt_gatt_attr *attr,
                                   uint16_t value)
{
    gait_data_notify_enabled = (value == BT_GATT_CCC_NOTIFY);
    LOG_INF("Gait data notifications %s",
            gait_data_notify_enabled ? "enabled" : "disabled");
}

/* ---------------------------------------------------------------------------
 * Config characteristic callbacks
 * -------------------------------------------------------------------------*/
static ssize_t config_read_cb(struct bt_conn *conn,
                               const struct bt_gatt_attr *attr,
                               void *buf, uint16_t len, uint16_t offset)
{
    return bt_gatt_attr_read(conn, attr, buf, len, offset,
                             &current_config, sizeof(current_config));
}

static ssize_t config_write_cb(struct bt_conn *conn,
                                const struct bt_gatt_attr *attr,
                                const void *buf, uint16_t len,
                                uint16_t offset, uint8_t flags)
{
    if (offset + len > sizeof(current_config)) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }

    memcpy((uint8_t *)&current_config + offset, buf, len);
    LOG_INF("Config updated: IMU=%dHz FSR=%dHz notify=%dHz",
            current_config.imu_rate_hz,
            current_config.fsr_rate_hz,
            current_config.notify_rate_hz);

    return len;
}

/* ---------------------------------------------------------------------------
 * Device Info characteristic callback
 * -------------------------------------------------------------------------*/
static ssize_t device_info_read_cb(struct bt_conn *conn,
                                    const struct bt_gatt_attr *attr,
                                    void *buf, uint16_t len, uint16_t offset)
{
    return bt_gatt_attr_read(conn, attr, buf, len, offset,
                             &dev_info, sizeof(dev_info));
}

/* ---------------------------------------------------------------------------
 * GATT Service Definition
 * -------------------------------------------------------------------------*/
BT_GATT_SERVICE_DEFINE(gait_svc,
    /* Primary Service Declaration */
    BT_GATT_PRIMARY_SERVICE(&gait_service_uuid),

    /* Characteristic 1: Gait Data (notify only) */
    BT_GATT_CHARACTERISTIC(&gait_data_uuid.uuid,
                           BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_NONE,
                           NULL, NULL, NULL),
    BT_GATT_CCC(gait_data_ccc_changed,
                 BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),

    /* Characteristic 2: Config (read + write) */
    BT_GATT_CHARACTERISTIC(&config_uuid.uuid,
                           BT_GATT_CHRC_READ | BT_GATT_CHRC_WRITE,
                           BT_GATT_PERM_READ | BT_GATT_PERM_WRITE,
                           config_read_cb, config_write_cb, &current_config),

    /* Characteristic 3: Device Info (read only) */
    BT_GATT_CHARACTERISTIC(&device_info_uuid.uuid,
                           BT_GATT_CHRC_READ,
                           BT_GATT_PERM_READ,
                           device_info_read_cb, NULL, &dev_info),
);

/* ---------------------------------------------------------------------------
 * Public API
 * -------------------------------------------------------------------------*/

int gait_service_init(void)
{
    LOG_INF("Gait GATT service registered");
    return 0;
}

int gait_service_notify(struct gait_data_packet *pkt)
{
    if (!gait_data_notify_enabled) {
        return -EACCES;
    }

    /* Attribute index: service decl (0), char decl (1), char value (2) */
    const struct bt_gatt_attr *attr = &gait_svc.attrs[2];

    int ret = bt_gatt_notify(NULL, attr, pkt, sizeof(*pkt));
    if (ret < 0 && ret != -ENOTCONN) {
        LOG_DBG("Notify failed: %d", ret);
    }

    return ret;
}
