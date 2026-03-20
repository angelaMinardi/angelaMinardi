/*
 * Smart Insole - BLE Connection Manager
 *
 * Manages BLE advertising, connection lifecycle, MTU exchange,
 * and connection parameters.
 */

#include "ble_manager.h"

#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/hci.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(ble_manager, CONFIG_LOG_DEFAULT_LEVEL);

/* ---------------------------------------------------------------------------
 * Connection state
 * -------------------------------------------------------------------------*/
static struct bt_conn *current_conn;
static bool connected;

/* ---------------------------------------------------------------------------
 * Advertising data
 * -------------------------------------------------------------------------*/
static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS,
                  (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE,
            CONFIG_BT_DEVICE_NAME,
            sizeof(CONFIG_BT_DEVICE_NAME) - 1),
};

/* Scan response: include custom service UUID */
static const uint8_t svc_uuid_bytes[] = {
    /* 12345678-1234-5678-1234-56789abcdef0  (little-endian) */
    0xf0, 0xde, 0xbc, 0x9a, 0x78, 0x56, 0x34, 0x12,
    0x78, 0x56, 0x34, 0x12, 0x78, 0x56, 0x34, 0x12,
};

static const struct bt_data sd[] = {
    BT_DATA(BT_DATA_UUID128_ALL, svc_uuid_bytes, sizeof(svc_uuid_bytes)),
};

/* ---------------------------------------------------------------------------
 * Desired connection parameters
 *   Interval: 15 ms (12 * 1.25 ms)
 *   Latency:  0
 *   Timeout:  4 s  (400 * 10 ms)
 * -------------------------------------------------------------------------*/
#define CONN_INTERVAL_MIN   12   /* 15.0 ms  */
#define CONN_INTERVAL_MAX   12   /* 15.0 ms  */
#define CONN_LATENCY        0
#define CONN_TIMEOUT        400  /* 4000 ms  */

static struct bt_le_conn_param conn_params = BT_LE_CONN_PARAM_INIT(
    CONN_INTERVAL_MIN, CONN_INTERVAL_MAX, CONN_LATENCY, CONN_TIMEOUT);

/* ---------------------------------------------------------------------------
 * MTU exchange callback
 * -------------------------------------------------------------------------*/
static void mtu_exchange_cb(struct bt_conn *conn, uint8_t err,
                             struct bt_gatt_exchange_params *params)
{
    if (err) {
        LOG_WRN("MTU exchange failed (err %u)", err);
    } else {
        uint16_t mtu = bt_gatt_get_mtu(conn);
        LOG_INF("MTU exchanged: %u", mtu);
    }
}

static struct bt_gatt_exchange_params mtu_exchange_params = {
    .func = mtu_exchange_cb,
};

/* ---------------------------------------------------------------------------
 * Connection callbacks
 * -------------------------------------------------------------------------*/
static void on_connected(struct bt_conn *conn, uint8_t err)
{
    if (err) {
        LOG_ERR("Connection failed (err %u)", err);
        return;
    }

    char addr_str[BT_ADDR_LE_STR_LEN];
    bt_addr_le_to_str(bt_conn_get_dst(conn), addr_str, sizeof(addr_str));
    LOG_INF("Connected: %s", addr_str);

    current_conn = bt_conn_ref(conn);
    connected = true;

    /* Request desired connection parameters */
    int ret = bt_conn_le_param_update(conn, &conn_params);
    if (ret < 0) {
        LOG_WRN("Conn param update request failed: %d", ret);
    }

    /* Initiate MTU exchange for 247-byte MTU */
    ret = bt_gatt_exchange_mtu(conn, &mtu_exchange_params);
    if (ret < 0) {
        LOG_WRN("MTU exchange request failed: %d", ret);
    }
}

static void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
    char addr_str[BT_ADDR_LE_STR_LEN];
    bt_addr_le_to_str(bt_conn_get_dst(conn), addr_str, sizeof(addr_str));
    LOG_INF("Disconnected: %s (reason %u)", addr_str, reason);

    if (current_conn) {
        bt_conn_unref(current_conn);
        current_conn = NULL;
    }
    connected = false;

    /* Automatically restart advertising */
    int ret = ble_manager_start_advertising();
    if (ret < 0) {
        LOG_ERR("Failed to restart advertising: %d", ret);
    }
}

static void on_le_param_updated(struct bt_conn *conn, uint16_t interval,
                                 uint16_t latency, uint16_t timeout)
{
    LOG_INF("Conn params updated: interval=%u latency=%u timeout=%u",
            interval, latency, timeout);
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
    .connected        = on_connected,
    .disconnected     = on_disconnected,
    .le_param_updated = on_le_param_updated,
};

/* ---------------------------------------------------------------------------
 * Public API
 * -------------------------------------------------------------------------*/

int ble_manager_init(void)
{
    int ret;

    connected    = false;
    current_conn = NULL;

    ret = bt_enable(NULL);
    if (ret < 0) {
        LOG_ERR("Bluetooth enable failed: %d", ret);
        return ret;
    }

    LOG_INF("BLE subsystem initialised");
    return 0;
}

int ble_manager_start_advertising(void)
{
    int ret;

    struct bt_le_adv_param adv_params = *BT_LE_ADV_CONN;
    adv_params.interval_min = BT_GAP_ADV_FAST_INT_MIN_2;
    adv_params.interval_max = BT_GAP_ADV_FAST_INT_MAX_2;

    ret = bt_le_adv_start(&adv_params,
                          ad, ARRAY_SIZE(ad),
                          sd, ARRAY_SIZE(sd));
    if (ret < 0 && ret != -EALREADY) {
        LOG_ERR("Advertising start failed: %d", ret);
        return ret;
    }

    LOG_INF("BLE advertising started");
    return 0;
}

int ble_manager_stop_advertising(void)
{
    int ret = bt_le_adv_stop();
    if (ret < 0) {
        LOG_WRN("Advertising stop failed: %d", ret);
    }
    return ret;
}

bool ble_is_connected(void)
{
    return connected;
}
