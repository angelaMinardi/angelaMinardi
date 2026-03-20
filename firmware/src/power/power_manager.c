/*
 * Smart Insole - Power Management
 *
 * Battery monitoring via ADC voltage divider, idle detection,
 * and deep sleep with IMU motion wakeup.
 */

#include "power_manager.h"

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/pm/pm.h>
#include <zephyr/pm/device.h>
#include <zephyr/logging/log.h>
#include <zephyr/sys/poweroff.h>

LOG_MODULE_REGISTER(power_mgr, CONFIG_LOG_DEFAULT_LEVEL);

/* ---------- Battery ADC configuration ---------- */

#define BATTERY_ADC_NODE       DT_NODELABEL(adc)
#define BATTERY_ADC_CHANNEL    7
#define BATTERY_ADC_RESOLUTION 12
#define BATTERY_ADC_GAIN       ADC_GAIN_1_6
#define BATTERY_ADC_REFERENCE  ADC_REF_INTERNAL

/* 0.6V internal ref with 1/6 gain => max 3.6V on ADC pin.
 * Through voltage divider (2x 100k), max battery = 7.2V. */
#define V_REF_MV        600
#define ADC_GAIN_FACTOR 6
#define DIVIDER_FACTOR  2
#define ADC_MAX_VAL     ((1 << BATTERY_ADC_RESOLUTION) - 1)

static const struct device *adc_dev;
static int16_t adc_buf;

static struct adc_channel_cfg channel_cfg = {
    .gain             = BATTERY_ADC_GAIN,
    .reference        = BATTERY_ADC_REFERENCE,
    .acquisition_time = ADC_ACQ_TIME(ADC_ACQ_TIME_MICROSECONDS, 40),
    .channel_id       = BATTERY_ADC_CHANNEL,
    .input_positive   = SAADC_CH_PSELP_PSELP_AnalogInput7,
};

static struct adc_sequence sequence = {
    .channels    = BIT(BATTERY_ADC_CHANNEL),
    .buffer      = &adc_buf,
    .buffer_size = sizeof(adc_buf),
    .resolution  = BATTERY_ADC_RESOLUTION,
};

/* ---------- Idle tracking ---------- */

#define IDLE_TIMEOUT_MS  (5 * 60 * 1000)  /* 5 minutes */

static int64_t last_motion_time;
static bool    initialized;

/* ---------- LiPo discharge curve lookup ---------- */

struct voltage_pct {
    uint16_t mv;
    uint8_t  pct;
};

static const struct voltage_pct discharge_curve[] = {
    { 4200, 100 }, { 4150,  95 }, { 4110,  90 }, { 4080,  85 },
    { 4020,  80 }, { 3980,  75 }, { 3920,  70 }, { 3870,  65 },
    { 3820,  60 }, { 3790,  55 }, { 3770,  50 }, { 3750,  45 },
    { 3730,  40 }, { 3710,  35 }, { 3690,  30 }, { 3610,  25 },
    { 3530,  20 }, { 3450,  15 }, { 3370,  10 }, { 3280,   5 },
    { 3000,   0 },
};

#define CURVE_LEN (sizeof(discharge_curve) / sizeof(discharge_curve[0]))

static uint8_t voltage_to_pct(uint16_t mv)
{
    if (mv >= discharge_curve[0].mv) {
        return 100;
    }
    if (mv <= discharge_curve[CURVE_LEN - 1].mv) {
        return 0;
    }

    for (size_t i = 0; i < CURVE_LEN - 1; i++) {
        if (mv >= discharge_curve[i + 1].mv) {
            uint16_t v_high = discharge_curve[i].mv;
            uint16_t v_low  = discharge_curve[i + 1].mv;
            uint8_t  p_high = discharge_curve[i].pct;
            uint8_t  p_low  = discharge_curve[i + 1].pct;
            uint16_t dv = v_high - v_low;
            if (dv == 0) {
                return p_high;
            }
            return p_low +
                   (uint8_t)(((uint32_t)(mv - v_low) * (p_high - p_low)) / dv);
        }
    }
    return 0;
}

/* ---------- Public API ---------- */

int power_manager_init(void)
{
    adc_dev = DEVICE_DT_GET(BATTERY_ADC_NODE);
    if (!device_is_ready(adc_dev)) {
        LOG_ERR("ADC device not ready");
        return -ENODEV;
    }

    int err = adc_channel_setup(adc_dev, &channel_cfg);
    if (err) {
        LOG_ERR("ADC channel setup failed: %d", err);
        return err;
    }

    last_motion_time = k_uptime_get();
    initialized = true;

    LOG_INF("Power manager initialized");
    return 0;
}

uint8_t power_get_battery_pct(void)
{
    if (!initialized || !adc_dev) {
        return 0;
    }

    int err = adc_read(adc_dev, &sequence);
    if (err) {
        LOG_WRN("ADC read failed: %d", err);
        return 0;
    }

    /* Convert ADC raw value to battery voltage in mV */
    int32_t adc_mv = (int32_t)adc_buf;
    adc_mv = (adc_mv * V_REF_MV * ADC_GAIN_FACTOR) / ADC_MAX_VAL;
    uint16_t battery_mv = (uint16_t)(adc_mv * DIVIDER_FACTOR);

    LOG_DBG("Battery: %u mV (ADC raw: %d)", battery_mv, adc_buf);

    return voltage_to_pct(battery_mv);
}

void power_report_motion(void)
{
    last_motion_time = k_uptime_get();
}

void power_check_idle(void)
{
    if (!initialized) {
        return;
    }

    int64_t now = k_uptime_get();
    int64_t idle_ms = now - last_motion_time;

    if (idle_ms >= IDLE_TIMEOUT_MS) {
        LOG_INF("Idle for %lld ms, entering System OFF", idle_ms);

        /* IMU INT1 configured as wakeup source in device tree.
         * BMI270 any-motion interrupt will trigger reset-wakeup. */
        k_sleep(K_MSEC(100));

        /* Enter System OFF (~0.4 uA on nRF52840).
         * Device resets on wakeup via GPIO interrupt. */
        sys_poweroff();

        LOG_ERR("Failed to enter deep sleep");
    }
}

void power_enter_shipping_mode(void)
{
    LOG_INF("Entering shipping mode (ultra-deep sleep)");
    k_sleep(K_MSEC(100));
    sys_poweroff();
}
