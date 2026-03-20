# Smart Insole - PCB Layout Specifications

## 1. Two-Board Architecture

The insole uses a two-board approach to balance rigidity (for electronics) with flexibility (for pressure sensing across the foot sole).

### 1.1 Rigid PCB (Heel Pocket Module)

**Dimensions**: 25mm x 18mm x 1.6mm (4-layer)

**Layer Stackup**:
```
Layer 1 (Top):    Signal + Components     (35um Cu)
Layer 2 (Inner):  Ground plane            (35um Cu)
Layer 3 (Inner):  Power plane (3V3/BAT)   (35um Cu)
Layer 4 (Bottom): Signal + Components     (35um Cu)

Dielectric: FR-4, Er=4.2
Core thickness: 0.8mm (between L2-L3)
Prepreg: 0.2mm (L1-L2, L3-L4)
Total: ~1.6mm
```

**Top Side Component Placement**:
```
  ┌──────────────────────────┐
  │  ┌─────┐    ┌────┐      │
  │  │nRF  │    │BMI │      │
  │  │52840│    │270 │ ANT  │
  │  │     │    └────┘ ┌──┐ │
  │  │     │           │  │ │
  │  └─────┘  ┌────┐  └──┘ │
  │           │MUX │        │
  │  [DEBUG]  │4051│  [FPC] │
  │           └────┘        │
  └──────────────────────────┘
       25mm
```

**Bottom Side Component Placement**:
```
  ┌──────────────────────────┐
  │  ┌──────┐   ┌──────┐    │
  │  │MCP   │   │TPS   │    │
  │  │73831 │   │62740 │    │
  │  │      │   │      │    │
  │  └──────┘   └──────┘    │
  │                          │
  │  ┌──────────────┐ [TMP] │
  │  │   USB-C      │ [117] │
  │  └──────────────┘       │
  └──────────────────────────┘
```

**Antenna Keepout Zone**:
- 5mm ground clearance on ALL copper layers around the Johanson 2450AT18x100
- No ground pour, traces, or vias within the keepout zone
- Antenna placed at board edge for optimal radiation pattern
- Ground plane extends to edge of keepout zone (acts as ground plane reflector)

### 1.2 Flex PCB (Foot Sole Sensor Array)

**Material**: Polyimide (Kapton) flexible circuit

**Specifications**:
```
Substrate:   25um polyimide (Kapton HN)
Copper:      18um (0.5 oz) rolled annealed copper, 2 layers
Coverlay:    25um polyimide + 25um adhesive
Total:       ~0.12mm thickness
```

**Outline**: Contoured to foot sole shape. Available in sizes:
- Small (US 7-8): 245mm x 85mm
- Medium (US 9-10): 265mm x 92mm
- Large (US 11-12): 280mm x 100mm

**FSR Pad Positions** (relative to heel center, medium size):

```
                    ┌──── BIG TOE (FSR7)
                    │     x:35mm y:235mm, pad:15mm dia
                    │
          ┌─────────┼────── 1st META (FSR4)
          │         │       x:25mm y:190mm
          │    ┌────┼────── 3rd META (FSR5)
          │    │    │       x:46mm y:180mm
          │    │    │  ┌─── 5th META (FSR6)
          │    │    │  │    x:67mm y:185mm
          │    │    │  │
          │    │    │  │
          │    │    │  │
          └────┴────┴──┘
               │
          MIDFOOT ARCH (FSR3)
          x:38mm y:120mm
               │
               │
          ┌────┴────┐
     HEEL │  CENTER  │ HEEL
     MED  │  (FSR0)  │ LAT
    (FSR1)│ x:46mm   │(FSR2)
    x:30mm│ y:30mm   │x:62mm
    y:25mm│          │y:25mm
          └──────────┘

  Trace routing: All traces run along medial edge
  to FPC connector at heel
```

**Flex PCB Design Rules**:
- Minimum trace width: 0.15mm (signal), 0.3mm (power/FSR)
- Minimum trace spacing: 0.15mm
- Minimum bend radius: 1.0mm (static bend), 3.0mm (dynamic bend)
- Via size: 0.3mm drill, 0.6mm pad (use sparingly on flex)
- Stiffener: 0.2mm polyimide stiffener behind each FSR pad area

### 1.3 FPC Connector Interface

```
Flex PCB side: 10-pin FPC tail (0.5mm pitch)
Rigid PCB side: Molex 5035651092 bottom-contact ZIF connector

Pin Assignment:
  Pin 1:  FSR0 (Heel Center)
  Pin 2:  FSR1 (Heel Medial)
  Pin 3:  FSR2 (Heel Lateral)
  Pin 4:  FSR3 (Midfoot Arch)
  Pin 5:  FSR4 (1st Metatarsal)
  Pin 6:  FSR5 (3rd Metatarsal)
  Pin 7:  FSR6 (5th Metatarsal)
  Pin 8:  FSR7 (Big Toe)
  Pin 9:  3V3 (power for FSR dividers)
  Pin 10: GND
```

## 2. Design Rules (Rigid PCB)

| Parameter | Value |
|---|---|
| Minimum trace width | 0.15mm (signal), 0.25mm (power) |
| Minimum trace spacing | 0.15mm |
| Minimum via drill | 0.25mm |
| Via pad diameter | 0.5mm |
| Minimum annular ring | 0.125mm |
| Copper-to-edge clearance | 0.3mm |
| Surface finish | ENIG (Electroless Nickel Immersion Gold) |
| Solder mask color | Matte black |
| Silkscreen | White |
| Board thickness | 1.6mm |

## 3. Controlled Impedance

```
50-ohm single-ended (for antenna feed):
  Layer 1, over L2 ground plane
  Trace width: 0.30mm (calculated for FR-4 Er=4.2, 0.2mm prepreg)

  Only required for the ~3mm trace from nRF52840 ANT pin to matching network.
```

## 4. Assembly Notes

### 4.1 Rigid PCB Assembly
- Standard SMT reflow (lead-free SAC305)
- Bottom side assembled first (USB-C, charger, regulator, TMP117)
- Top side assembled second (nRF52840, BMI270, MUX, passives)
- SWD debug pads: Tag-Connect TC2050 footprint (no permanent header)

### 4.2 Flex-to-Rigid Connection
- FPC tail inserts into ZIF connector on rigid PCB
- Lock tab secures connection
- Strain relief: 5mm radius bend at connection point

### 4.3 Encapsulation (IP67)
- Rigid PCB module: potted in silicone (Dow DOWSIL 3-4207) in a 3D-printed TPU shell
- Shell dimensions: 28mm x 21mm x 8mm (fits in heel cavity of shoe insole)
- Battery compartment within shell, replaceable via bottom cover with silicone gasket
- Flex PCB: laminated between two layers of medical-grade silicone sheet (0.5mm each)
- FSR sensing areas: thin silicone (0.3mm) to maintain pressure sensitivity
- Total insole thickness: ~3.5mm (comparable to standard shoe insole)

## 5. Mechanical Integration

```
                  SHOE INSOLE CROSS-SECTION (heel area)

              ┌─────────────────────────────────────┐
              │         Standard foam insole         │ ~2mm
              ├─────────────────────────────────────┤
              │     Silicone-encapsulated flex PCB   │ ~1.5mm
              │     (FSR traces + coverlay)          │
              ├─────────┬───────────┬───────────────┤
              │         │ Rigid PCB │               │
              │  Foam   │ module    │    Foam       │ ~8mm at heel
              │         │ + battery │               │
              │         │ in TPU    │               │
              │         │ shell     │               │
              ├─────────┴───────────┴───────────────┤
              │         Bottom sole contact          │ ~1mm
              └─────────────────────────────────────┘
```

## 6. Manufacturing Files

For production, generate these files from KiCad (when detailed layout is complete):
- Gerber files (RS-274X): Top/Bottom copper, solder mask, silkscreen, drill
- NC drill file (Excellon format)
- Pick-and-place file (component XY coordinates + rotation)
- BOM (see `bom.csv`)
- Assembly drawings (PDF)
- 3D STEP model for mechanical integration check
