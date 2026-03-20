/*
 * Smart Insole - FSR Array Driver
 *
 * Reads 8 FSR sensors through a CD74HC4051 8:1 analog MUX.
 * MUX select lines S0/S1/S2 are controlled via GPIO; the common
 * output is read through the nRF52840 SAADC on AIN0.
 *
 * Voltage divider: V_out = V_supply * R_pulldown / (R_FSR + R_pulldown)
 * Pull-down resistor: 10 kOhm
 * V_supply: 3.3 V (nRF52840 VDD)
 */

#include "fsr.h"

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>
#include <math.h>

LOG_MODULE_REGISTER(fsr, CONFIG_LOG_DEFAULT_LEVEL);

/* ---------------------------------------------------------------------------
 * Hardware constants
 * -------------------------------------------------------------------------*/
#define V_SUPPLY         3.3f
#define R_PULLDOWN       10000.0f   /* 10 kOhm pull-down */
#define ADC_RESOLUTION   12
#define ADC_MAX_VALUE    4095       /* 2^12 - 1 */

/* Internal reference 0.6 V with 1/6 gain => full-scale = 3.6 V */
#define ADC_REF_VOLTAGE  3.6f

/* MUX settling time (microseconds) after channel change */
#define MUX_SETTLE_US    10

/* ---------------------------------------------------------------------------
 * GPIO specs for MUX select lines (from device tree)
 * -------------------------------------------------------------------------*/
#define MUX_S0_NODE  DT_NODELABEL(mux_s0)
#define MUX_S1_NODE  DT_NODELABEL(mux_s1)
#define MUX_S2_NODE  DT_NODELABEL(mux_s2)

static const struct gpio_dt_spec mux_s0 = GPIO_DT_SPEC_GET(MUX_S0_NODE, gpios);
static const struct gpio_dt_spec mux_s1 = GPIO_DT_SPEC_GET(MUX_S1_NODE, gpios);
static const struct gpio_dt_spec mux_s2 = GPIO_DT_SPEC_GET(MUX_S2_NODE, gpios);

/* ---------------------------------------------------------------------------
 * ADC configuration
 * -------------------------------------------------------------------------*/
#define ADC_NODE  DT_NODELABEL(adc)
static const struct device *adc_dev = DEVICE_DT_GET(ADC_NODE);

static int16_t adc_sample_buffer;

static const struct adc_channel_cfg adc_ch_cfg = {
    .gain             = ADC_GAIN_1_6,
    .reference        = ADC_REF_INTERNAL,
    .acquisition_time = ADC_ACQ_TIME(ADC_ACQ_TIME_MICROSECONDS, 40),
    .channel_id       = 0,
    .input_positive   = SAADC_CH_PSELP_PSELP_AnalogInput0,
};

static struct adc_sequence adc_seq = {
    .channels    = BIT(0),
    .buffer      = &adc_sample_buffer,
    .buffer_size = sizeof(adc_sample_buffer),
    .resolution  = ADC_RESOLUTION,
};

/* ---------------------------------------------------------------------------
 * FSR 402 piecewise-linear lookup table
 * Maps R_FSR (Ohms) -> Force (N).  Derived from Interlink FSR 402 datasheet.
 * -------------------------------------------------------------------------*/
struct fsr_lut_entry {
    float resistance; /* Ohms */
    float force;      /* Newtons */
};

static const struct fsr_lut_entry fsr_lut[] = {
    { 1000000.0f,  0.0f  },
    { 100000.0f,   0.2f  },
    { 30000.0f,    1.0f  },
    { 10000.0f,    3.0f  },
    { 3000.0f,    10.0f  },
    { 1000.0f,    30.0f  },
    { 500.0f,     60.0f  },
    { 250.0f,    100.0f  },
};

#define FSR_LUT_SIZE  (sizeof(fsr_lut) / sizeof(fsr_lut[0]))

/* Zone names */
static const char *zone_names[FSR_CHANNEL_COUNT] = {
    "HEEL_CENTER",
    "HEEL_MEDIAL",
    "HEEL_LATERAL",
    "MIDFOOT_ARCH",
    "META_1ST",
    "META_3RD",
    "META_5TH",
    "BIG_TOE",
};

/* ---------------------------------------------------------------------------
 * Public API
 * -------------------------------------------------------------------------*/

int fsr_init(void)
{
    int ret;

    /* Verify ADC device is ready */
    if (!device_is_ready(adc_dev)) {
        LOG_ERR("ADC device not ready");
        return -ENODEV;
    }

    /* Configure ADC channel */
    ret = adc_channel_setup(adc_dev, &adc_ch_cfg);
    if (ret < 0) {
        LOG_ERR("ADC channel setup failed: %d", ret);
        return ret;
    }

    /* Configure MUX select GPIOs as outputs */
    if (!gpio_is_ready_dt(&mux_s0) ||
        !gpio_is_ready_dt(&mux_s1) ||
        !gpio_is_ready_dt(&mux_s2)) {
        LOG_ERR("MUX GPIO device not ready");
        return -ENODEV;
    }

    ret = gpio_pin_configure_dt(&mux_s0, GPIO_OUTPUT_LOW);
    if (ret < 0) { return ret; }

    ret = gpio_pin_configure_dt(&mux_s1, GPIO_OUTPUT_LOW);
    if (ret < 0) { return ret; }

    ret = gpio_pin_configure_dt(&mux_s2, GPIO_OUTPUT_LOW);
    if (ret < 0) { return ret; }

    LOG_INF("FSR driver initialised (8-ch MUX + ADC)");
    return 0;
}

/**
 * Set the MUX channel (0-7) by driving S0, S1, S2.
 */
static void mux_select_channel(uint8_t channel)
{
    gpio_pin_set_dt(&mux_s0, (channel >> 0) & 0x01);
    gpio_pin_set_dt(&mux_s1, (channel >> 1) & 0x01);
    gpio_pin_set_dt(&mux_s2, (channel >> 2) & 0x01);
}

/**
 * Read the ADC once and return the raw 12-bit value.
 */
static int adc_read_raw(uint16_t *value)
{
    int ret = adc_read(adc_dev, &adc_seq);
    if (ret < 0) {
        return ret;
    }

    /* SAADC can return negative values in differential mode; clamp to 0. */
    *value = (adc_sample_buffer < 0) ? 0 : (uint16_t)adc_sample_buffer;
    return 0;
}

int fsr_read_all(uint16_t values[FSR_CHANNEL_COUNT])
{
    int ret;

    for (uint8_t ch = 0; ch < FSR_CHANNEL_COUNT; ch++) {
        mux_select_channel(ch);
        k_busy_wait(MUX_SETTLE_US);

        ret = adc_read_raw(&values[ch]);
        if (ret < 0) {
            LOG_WRN("ADC read failed on MUX ch %u: %d", ch, ret);
            values[ch] = 0;
        }
    }

    return 0;
}

float fsr_to_force(uint16_t adc_value)
{
    if (adc_value == 0) {
        return 0.0f;
    }

    /* Convert ADC count to voltage */
    float v_measured = ((float)adc_value / (float)ADC_MAX_VALUE) * ADC_REF_VOLTAGE;

    /* Clamp to avoid division issues */
    if (v_measured >= V_SUPPLY) {
        v_measured = V_SUPPLY - 0.001f;
    }

    /* Calculate FSR resistance from voltage divider equation:
     *   V_out = V_supply * R_pulldown / (R_FSR + R_pulldown)
     *   R_FSR = R_pulldown * (V_supply / V_out - 1)
     */
    float r_fsr = R_PULLDOWN * ((V_SUPPLY / v_measured) - 1.0f);

    /* If resistance is extremely high, no meaningful force */
    if (r_fsr >= fsr_lut[0].resistance) {
        return 0.0f;
    }

    /* Piecewise linear interpolation on log-log scale (FSR characteristic) */
    for (int i = 0; i < (int)FSR_LUT_SIZE - 1; i++) {
        if (r_fsr <= fsr_lut[i].resistance && r_fsr >= fsr_lut[i + 1].resistance) {
            float log_r  = logf(r_fsr);
            float log_r0 = logf(fsr_lut[i].resistance);
            float log_r1 = logf(fsr_lut[i + 1].resistance);

            float f0 = fsr_lut[i].force;
            float f1 = fsr_lut[i + 1].force;

            /* Handle the first segment where f0 is 0 N */
            if (f0 < 0.001f) {
                float t = (log_r0 - log_r) / (log_r0 - log_r1);
                return f1 * t;
            }

            float log_f0 = logf(f0);
            float log_f1 = logf(f1);

            float t = (log_r0 - log_r) / (log_r0 - log_r1);
            return expf(log_f0 + t * (log_f1 - log_f0));
        }
    }

    /* Below minimum resistance in table -> return max force */
    return fsr_lut[FSR_LUT_SIZE - 1].force;
}

const char *fsr_zone_name(enum fsr_zone zone)
{
    if (zone >= FSR_CHANNEL_COUNT) {
        return "UNKNOWN";
    }
    return zone_names[zone];
}
