# Smart Insole - Circuit Schematic

## 1. Power Management

### 1.1 USB-C Input (USB4110-GF-A)

```
USB-C Connector (USB4110-GF-A)
  VBUS ──┬── ESD (PRTR5V0U2X) ──┬── MCP73831 VDD (pin 4)
         │                       └── Schottky diode ── 5V_USB net
  D+   ──┼── PRTR5V0U2X ── (unused for data, charge only)
  D-   ──┼── PRTR5V0U2X ── (unused for data, charge only)
  GND  ──┴── GND
  CC1  ── 5.1k to GND (identifies as UFP/sink)
  CC2  ── 5.1k to GND
  SHIELD ── GND via 1M + 100pF (EMI filtering)
```

### 1.2 Battery Charger (MCP73831T-2ACI/OT)

```
                    MCP73831
                  ┌──────────┐
  5V_USB ─────────┤ VDD    4 │
                  │          │
  BAT+ ──────────┤ VBAT   3 │──── Battery + (3.7V LiPo 150mAh)
                  │          │
  GND ───────────┤ VSS    2 │
                  │          │
  RPROG ─────────┤ PROG   5 │── 2.0k to GND (I_charge = 1000/R = 500mA)
                  │          │
  STAT_LED ──────┤ STAT   1 │── 470R ── LED ── GND (charge indicator)
                  └──────────┘

  VBAT net: 4.7uF ceramic cap to GND (C1)
  VDD net:  4.7uF ceramic cap to GND (C2)
```

### 1.3 Voltage Regulator (TPS62740DSSR)

```
                    TPS62740
                  ┌──────────────┐
  BAT+ ──────────┤ VIN        1 │──── 10uF ceramic (C3) to GND
                  │              │
  3.3V ──────────┤ VOUT       5 │──── 10uF ceramic (C4) to GND
                  │              │           │
  GND ───────────┤ GND        3 │           └── 3V3 rail (all logic)
                  │              │
  100k to BAT+ ──┤ EN         2 │  (always enabled)
                  │              │
                  │ VSEL1      6 │── VDD (3.3V output select)
                  │ VSEL2      7 │── GND
                  │ VSEL3      8 │── VDD
                  │              │
                  │ SW         4 │── 2.2uH inductor ── VOUT
                  └──────────────┘

  Output: 3.3V, 360nA quiescent current
```

### 1.4 Battery Voltage Monitoring

```
  BAT+ ── 100k (R1) ──┬── 100k (R2) ── GND
                       │
                       └── nRF52840 P0.31 (AIN7)

  V_adc = V_bat / 2   (range: 1.5V - 2.1V for 3.0-4.2V battery)
```

## 2. MCU (nRF52840-QIAA-R7)

### 2.1 Power Pins

```
  3V3 rail ──┬── VDD     (pin E23) ── 100nF (C5) to GND
             ├── VDD     (pin B1)  ── 100nF (C6) to GND
             ├── VDD     (pin D23) ── 100nF (C7) to GND
             ├── VDDH    (pin B6)  ── 1uF   (C8) to GND
             └── VBUS    (pin D1)  ── (connected to USB 5V for USB detection, or tie to VDD if no USB data)

  DEC1 (pin C1) ── 100nF (C9) to GND (internal regulator decoupling)
  DEC4 (pin A20) ── 1uF  (C10) to GND
  DEC5 (pin A16) ── 100pF (C11) to GND + 800pF (C12) to DEC6
  DEC6 (pin A14) ── (connected to C12 and DEC5)

  All VSS pins ── GND (A2, A4, B2, B22, C23, D2, E2)
```

### 2.2 Clock Crystals

```
  32 MHz Crystal (NX3225GD-32M-STD-CSR-4):
    X1 (pin B7) ── 12pF (C13) to GND
    X2 (pin A8) ── 12pF (C14) to GND

  32.768 kHz Crystal (ABS07-120-32.768KHZ-T):
    XL1 (pin B10) ── 6.8pF (C15) to GND
    XL2 (pin A10) ── 6.8pF (C16) to GND
```

### 2.3 Reset Circuit

```
  nRESET (pin A18) ──┬── 100nF (C17) to GND
                     └── 10k (R3) to VDD
```

### 2.4 SWD Debug Header (2x5 1.27mm)

```
  Pin 1: VDD (3V3)
  Pin 2: SWDIO  (nRF52840 SWDIO, pin A9)
  Pin 3: GND
  Pin 4: SWDCLK (nRF52840 SWDCLK, pin B11)
  Pin 5: GND
  Pin 6: NC
  Pin 7: NC
  Pin 8: NC
  Pin 9: GND
  Pin 10: nRESET (nRF52840 pin A18)
```

## 3. BLE RF / Antenna

### 3.1 Antenna Matching Network (PI filter per Nordic reference)

```
  nRF52840 ANT pin (pin H1) ──┬── 2.2pF (C18) to GND
                               │
                               └── 3.9nH (L1) ──┬── 1.5pF (C19) to GND
                                                 │
                                                 └── Johanson 2450AT18x100 chip antenna

  Ground plane: minimum 5mm keepout zone around antenna on all copper layers.
  Antenna feed trace: 50-ohm controlled impedance, as short as possible.
```

## 4. IMU (BMI270)

### 4.1 SPI Connection

```
                      BMI270
                    ┌──────────┐
  3V3 ──────────────┤ VDDIO  1 │── 100nF (C20) to GND
  1V8 or 3V3 ──────┤ VDD    2 │── 100nF (C21) to GND
  GND ──────────────┤ GND    3 │
                    │          │
  P0.15 (SCK) ─────┤ SCK    4 │  SPI clock (up to 10 MHz)
  P0.14 (MISO) ────┤ SDO    5 │  SPI data out (MISO)
  P0.13 (MOSI) ────┤ SDI    6 │  SPI data in (MOSI)
  P0.16 (CS) ──────┤ CSB    7 │  Chip select (active low)
                    │          │
  P0.17 ───────────┤ INT1   8 │  Data ready / FIFO watermark interrupt
  NC ──────────────┤ INT2   9 │  (unused, no connect)
                    │          │
  VDD ─────────────┤ SDO_AUX 10│  Pull high (SPI mode select)
                    └──────────┘

  Note: CSB must be pulled low during power-up to select SPI mode.
  INT1 configured as push-pull, active-high in firmware.
```

## 5. Temperature Sensor (TMP117AIDRVR)

### 5.1 I2C Connection

```
                     TMP117
                   ┌──────────┐
  3V3 ─────────────┤ V+     1 │── 100nF (C22) to GND
  GND ─────────────┤ GND    2 │
                   │          │
  P0.26 (SDA) ────┤ SDA    3 │── 4.7k (R4) pull-up to 3V3
  P0.27 (SCL) ────┤ SCL    4 │── 4.7k (R5) pull-up to 3V3
                   │          │
  GND ─────────────┤ ADD0   5 │  I2C address = 0x48
                   │          │
  P0.28 ───────────┤ ALERT  6 │  (optional, temperature alert interrupt)
                   └──────────┘

  I2C bus: 400 kHz (Fast mode)
  TMP117 accuracy: +/-0.1C from -20C to +50C
  Resolution: 0.0078125 C (16-bit)
```

## 6. FSR Array + Analog Multiplexer

### 6.1 FSR Voltage Dividers (x8)

```
  For each FSR (FSR0 through FSR7):

  3V3 ── FSR 402 ──┬── 10k (R_pd) ── GND
                    │
                    └── CD74HC4051 input (Y0..Y7)

  V_out = 3.3V * R_pd / (R_FSR + R_pd)
  At no force: R_FSR > 1M => V_out ~ 0V
  At max force: R_FSR ~ 200R => V_out ~ 3.23V
```

### 6.2 Analog Multiplexer (CD74HC4051M96)

```
                   CD74HC4051
                 ┌──────────────┐
  Y0 (FSR0) ────┤ Y0         1 │  Heel Center
  Y1 (FSR1) ────┤ Y1         2 │  Heel Medial
  Y2 (FSR2) ────┤ Y2         3 │  Heel Lateral
  Y3 (FSR3) ────┤ Y3         4 │  Midfoot Arch
  Y4 (FSR4) ────┤ Y4         5 │  1st Metatarsal Head
  Y5 (FSR5) ────┤ Y5         6 │  3rd Metatarsal Head
  Y6 (FSR6) ────┤ Y6         7 │  5th Metatarsal Head
  Y7 (FSR7) ────┤ Y7         8 │  Big Toe
                 │              │
  P0.02 (AIN0) ─┤ Z (COM)   9 │  Common output to ADC
                 │              │
  P0.03 ────────┤ S0        10 │  Channel select bit 0
  P0.04 ────────┤ S1        11 │  Channel select bit 1
  P0.05 ────────┤ S2        12 │  Channel select bit 2
                 │              │
  3V3 ──────────┤ VCC       16 │── 100nF (C23) to GND
  GND ──────────┤ GND       8  │
  GND ──────────┤ INH       15 │  (inhibit low = always active)
                 └──────────────┘
```

## 7. Complete GPIO Pin Assignment

| nRF52840 Pin | GPIO | Function | Direction | Notes |
|---|---|---|---|---|
| P0.02 | AIN0 | FSR MUX output (ADC) | Input (analog) | Via CD74HC4051 COM |
| P0.03 | GPIO | MUX S0 (select bit 0) | Output | Channel select |
| P0.04 | GPIO | MUX S1 (select bit 1) | Output | Channel select |
| P0.05 | GPIO | MUX S2 (select bit 2) | Output | Channel select |
| P0.13 | SPI1 MOSI | BMI270 SDI | Output | SPI data in |
| P0.14 | SPI1 MISO | BMI270 SDO | Input | SPI data out |
| P0.15 | SPI1 SCK | BMI270 SCK | Output | SPI clock |
| P0.16 | GPIO | BMI270 CSB | Output | SPI chip select |
| P0.17 | GPIO | BMI270 INT1 | Input (IRQ) | Data ready interrupt |
| P0.26 | I2C0 SDA | TMP117 SDA | Bidirectional | 4.7k pull-up |
| P0.27 | I2C0 SCL | TMP117 SCL | Output | 4.7k pull-up |
| P0.28 | GPIO | TMP117 ALERT | Input (IRQ) | Optional |
| P0.31 | AIN7 | Battery voltage | Input (analog) | Via 100k/100k divider |
| SWDIO | Debug | SWD data | Bidirectional | Debug header |
| SWDCLK | Debug | SWD clock | Input | Debug header |
| nRESET | Reset | System reset | Input | 10k pull-up + 100nF cap |
| ANT (H1) | RF | BLE antenna | Output | PI matching network |
| XC1/XC2 | Clock | 32MHz crystal | - | 12pF load caps |
| XL1/XL2 | Clock | 32.768kHz crystal | - | 6.8pF load caps |

## 8. Net List Summary

| Net Name | Connected To |
|---|---|
| BAT+ | LiPo +, MCP73831 VBAT, TPS62740 VIN, R1 (divider) |
| 3V3 | TPS62740 VOUT, all VDD pins, BMI270 VDDIO, TMP117 V+, FSR dividers, MUX VCC, pull-ups |
| GND | All grounds, all decoupling cap returns |
| 5V_USB | USB-C VBUS, MCP73831 VDD, ESD protection |
| SPI_SCK | P0.15 -> BMI270 SCK |
| SPI_MOSI | P0.13 -> BMI270 SDI |
| SPI_MISO | P0.14 -> BMI270 SDO |
| SPI_CS_IMU | P0.16 -> BMI270 CSB |
| IMU_INT1 | P0.17 -> BMI270 INT1 |
| I2C_SDA | P0.26 -> TMP117 SDA (4.7k pull-up to 3V3) |
| I2C_SCL | P0.27 -> TMP117 SCL (4.7k pull-up to 3V3) |
| MUX_OUT | CD74HC4051 Z -> P0.02 (AIN0) |
| MUX_S0 | P0.03 -> CD74HC4051 S0 |
| MUX_S1 | P0.04 -> CD74HC4051 S1 |
| MUX_S2 | P0.05 -> CD74HC4051 S2 |
| BAT_SENSE | R1/R2 junction -> P0.31 (AIN7) |
