/*
 * Smart Insole - TMP117 I2C Temperature Driver
 *
 * The TMP117 is a high-accuracy (+/-0.1 C) digital temperature sensor
 * from Texas Instruments.  I2C address 0x48 (ADD0 = GND).
 *
 * Resolution: 0.0078125 C / LSB  (16-bit signed result).
 * We convert to units of 0.01 C for integer representation.
 */

#include "temperature.h"

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(temperature, CONFIG_LOG_DEFAULT_LEVEL);

/* ---------------------------------------------------------------------------
 * TMP117 Register Map
 * -------------------------------------------------------------------------*/
#define TMP117_I2C_ADDR          0x48

#define TMP117_REG_TEMP_RESULT   0x00
#define TMP117_REG_CONFIGURATION 0x01
#define TMP117_REG_T_HIGH_LIMIT  0x02
#define TMP117_REG_T_LOW_LIMIT   0x03
#define TMP117_REG_EEPROM_UL     0x04
#define TMP117_REG_EEPROM1       0x05
#define TMP117_REG_EEPROM2       0x06
#define TMP117_REG_TEMP_OFFSET   0x07
#define TMP117_REG_EEPROM3       0x08
#define TMP117_REG_DEVICE_ID     0x0F

/* TMP117 Device ID */
#define TMP117_DEVICE_ID_VALUE   0x0117

/*
 * Configuration register bits:
 *   [11:10] MOD  = 11b  -> one-shot mode
 *   [9:7]   CONV = 000b -> 15.5 ms conversion
 *   [6:5]   AVG  = 00b  -> no averaging (fastest)
 *   Others  default
 *
 * Full 16-bit config word for one-shot: 0x0C00
 */
#define TMP117_CONFIG_ONESHOT    0x0C00

/* Data-ready flag in configuration register (bit 13) */
#define TMP117_CONFIG_DATA_READY  BIT(13)

/* LSB resolution in degrees Celsius */
#define TMP117_RESOLUTION        0.0078125f

/* ---------------------------------------------------------------------------
 * I2C device (from device tree)
 * -------------------------------------------------------------------------*/
#define I2C_NODE  DT_NODELABEL(i2c0)
static const struct device *i2c_dev = DEVICE_DT_GET(I2C_NODE);

/* ---------------------------------------------------------------------------
 * Helper functions
 * -------------------------------------------------------------------------*/

static int tmp117_write_reg16(uint8_t reg, uint16_t value)
{
    uint8_t buf[3];
    buf[0] = reg;
    buf[1] = (uint8_t)(value >> 8);   /* MSB first */
    buf[2] = (uint8_t)(value & 0xFF);

    return i2c_write(i2c_dev, buf, 3, TMP117_I2C_ADDR);
}

static int tmp117_read_reg16(uint8_t reg, uint16_t *value)
{
    uint8_t buf[2];
    int ret;

    ret = i2c_write_read(i2c_dev, TMP117_I2C_ADDR, &reg, 1, buf, 2);
    if (ret < 0) {
        return ret;
    }

    *value = ((uint16_t)buf[0] << 8) | buf[1];
    return 0;
}

/* ---------------------------------------------------------------------------
 * Public API
 * -------------------------------------------------------------------------*/

int temperature_init(void)
{
    int ret;
    uint16_t dev_id;

    if (!device_is_ready(i2c_dev)) {
        LOG_ERR("I2C device not ready");
        return -ENODEV;
    }

    /* Read and verify device ID */
    ret = tmp117_read_reg16(TMP117_REG_DEVICE_ID, &dev_id);
    if (ret < 0) {
        LOG_ERR("TMP117 device ID read failed: %d", ret);
        return ret;
    }

    if (dev_id != TMP117_DEVICE_ID_VALUE) {
        LOG_ERR("Unexpected TMP117 device ID: 0x%04x (expected 0x%04x)",
                dev_id, TMP117_DEVICE_ID_VALUE);
        return -EINVAL;
    }

    /* Configure for one-shot mode (lowest power) */
    ret = tmp117_write_reg16(TMP117_REG_CONFIGURATION, TMP117_CONFIG_ONESHOT);
    if (ret < 0) {
        LOG_ERR("TMP117 configuration write failed: %d", ret);
        return ret;
    }

    LOG_INF("TMP117 temperature sensor initialised (one-shot mode)");
    return 0;
}

int16_t temperature_read(void)
{
    int ret;
    uint16_t config;
    uint16_t raw;

    /* Trigger a one-shot conversion by writing config with one-shot bits set */
    ret = tmp117_write_reg16(TMP117_REG_CONFIGURATION, TMP117_CONFIG_ONESHOT);
    if (ret < 0) {
        LOG_ERR("Failed to trigger one-shot: %d", ret);
        return INT16_MIN;
    }

    /* Wait for conversion to complete (max 15.5 ms for no averaging) */
    k_msleep(16);

    /* Poll data-ready flag */
    ret = tmp117_read_reg16(TMP117_REG_CONFIGURATION, &config);
    if (ret < 0) {
        LOG_ERR("Config read failed: %d", ret);
        return INT16_MIN;
    }

    if (!(config & TMP117_CONFIG_DATA_READY)) {
        /* Extra wait and retry once */
        k_msleep(10);
        ret = tmp117_read_reg16(TMP117_REG_CONFIGURATION, &config);
        if (ret < 0 || !(config & TMP117_CONFIG_DATA_READY)) {
            LOG_WRN("TMP117 data not ready after timeout");
            return INT16_MIN;
        }
    }

    /* Read temperature result (16-bit signed, 0.0078125 C/LSB) */
    ret = tmp117_read_reg16(TMP117_REG_TEMP_RESULT, &raw);
    if (ret < 0) {
        LOG_ERR("Temperature read failed: %d", ret);
        return INT16_MIN;
    }

    /* Convert raw to 0.01 C units:
     *   temp_C = raw * 0.0078125
     *   temp_centideg = raw * 0.0078125 * 100 = raw * 0.78125
     *   To avoid float: temp_centideg = (raw * 100) / 128
     *     because 0.0078125 * 100 = 0.78125 = 100/128
     */
    int16_t raw_signed = (int16_t)raw;
    int32_t temp_centideg = ((int32_t)raw_signed * 100) / 128;

    /* Clamp to int16_t range */
    if (temp_centideg > INT16_MAX) {
        temp_centideg = INT16_MAX;
    } else if (temp_centideg < INT16_MIN) {
        temp_centideg = INT16_MIN;
    }

    return (int16_t)temp_centideg;
}
