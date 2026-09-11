# SEAS Solo-1 — Propulsion (FAA Part 103)

**Regulatory target:** [14 CFR Part 103](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-103) ultralight vehicle.

| Part 103 rule | Solo-1 design |
|---------------|---------------|
| Single occupant | Yes |
| Max empty weight **254 lb (115 kg)** | **115 kg** incl. batteries |
| Max speed **55 kt** | Software cap **102 km/h** |
| No night / IFR | Day VFR only |

**Endurance:** ~**20 min** at this mass budget (same class as Jetson ONE). **45 min is not compatible with Part 103** without a wing or hybrid — battery mass alone would exceed 254 lb empty.

Aircraft Spruce = airframe. Propulsion = below.

---

## Frozen Part 103 configuration

### 1. Propulsion — **4× T-MOTOR X-A12XL II-24S** (coaxial arm kits)

| Field | Value |
|-------|-------|
| Supplier | **T-MOTOR** |
| Part | **X-A12XL II-24S** Coaxial UAV Propulsion System |
| Qty | **4** (8 motors, 8× 120A ESC, props included) |
| Rated thrust | **28–34 kg/arm** (coaxial pair) |
| Coaxial quad MTOW | **~120 kg** published — **verify hover margin at 210 kg** with T-MOTOR before flight |
| Voltage | **20–24S** — spec **14S–16S pack** or **two 7S** split (match ESC voltage rating; confirm with T-MOTOR for 210 kg) |
| Arm tube | **50 mm** |
| Price | ~$1,000 / arm |
| Order | [shop.tmotor.com/products/x-a12xl-v2-24s-coaxial-uav-propulsion-system](https://shop.tmotor.com/products/x-a12xl-v2-24s-coaxial-uav-propulsion-system) |
| Contact | onlinesales@tmotor.com · WhatsApp **+86 180 7928 0718** |

> **Important:** Published MTOW for X-A12XL quad is below 210 kg. Before manned flight, require **written thrust test at 52.5 kg/arm** (210/4) on a thrust stand, or step up to **X-A14-24S** only if empty weight can stay ≤ 115 kg (unlikely). Part 103 + 210 kg MTOW is **experimental** — Jetson ONE operates outside US Part 103 empty-weight rules in practice.

**If thrust insufficient:** lighter pilot, shorter flight, or accept non–Part-103 experimental category.

### 2. Battery — **1× ~13.5 kWh Danergy pack (Molicel P60C)**

| Field | Value |
|-------|-------|
| Supplier | **Danergy** |
| Cell | **Molicel INR-21700-P60C** |
| Energy | **13.5 kWh** nominal (**~11.5 kWh** usable) |
| Target mass | **≤ 38 kg** (to hold **115 kg** empty with ~32 kg airframe + ~45 kg propulsion) |
| Voltage | **14S** nominal (~50.4 V) — Jetson-class |
| Discharge | **≥ 150 A** continuous |
| BMS | Smart **CAN** bus |
| Order | [danenergy.com](https://www.danenergy.com/catalog/lithium-ion-battery-packs/) — quote **“Solo-1 Part 103: 13.5 kWh 14S P60C, ≤38 kg, 600×350×180 mm”** |

Reference module: [14S8P 2.42 kWh](https://www.danenergy.com/catalog/lithium-ion-battery-packs/premium-high-power-molicel-p60c-li-ion-battery-48000mah-50-4v-144a-max-tn14s8p-p60c) — scale config with integrator.

**Swappable packs (optional):** two **~6.75 kWh** modules if each stays under weight budget for solo carry.

### 3. ESCs

**Included in X-A12XL kits** (24S FOC 120A × 2 per arm).

Spares: [Hobbywing XRotor Pro H200A 24S](https://www.hobbywing.com/en/products/xrotor-pro-h200a-24s-foc) or [XC-ESC CH200 v2](https://www.xc-esc.com/product/ch200-v2-esc-controller/).

### 4. Flight controller

| Item | Spec |
|------|------|
| **Cube Orange** or **Pixhawk 6X** | ArduPilot |
| Speed limit | Set **WPNAV_SPEED** / motor governor to **≤ 55 kt** |
| Mixing | Coaxial octo frame |

### 5. Charging

| Item | Spec |
|------|------|
| Input | **240 V AC** |
| Time | **~1 hr** @ 13.5 kWh (Jetson-class) |
| Connector | Per Danergy / **Anderson SB50** |

---

## Part 103 mass budget (must not exceed 115 kg empty)

| Component | kg | Notes |
|-----------|-----|-------|
| Aluminum spaceframe (Spruce) | 28 | Weigh every tube; drill lightening holes in gussets |
| 4× X-A12XL arm kits (w/ ESC) | 20 | ~5 kg/arm installed target |
| Battery pack | 38 | 13.5 kWh P60C — **largest line item** |
| Harness + BRS chute (Spruce) | 16 | Confirm chute minimum weight band |
| Avionics + wiring | 5 | Minimal harness |
| Props / guards (in kit) | 8 | Included in arm kit mass above |
| **Total empty** | **115** | **254 lb — Part 103 ceiling** |
| Pilot (max) | 95 | 210 kg MTOW |
| **MTOW** | **210** | |

Weigh aircraft **without pilot** before every annual check; add ballast chart in logbook.

---

## Energy budget (~20 min)

| Parameter | Value |
|-----------|-------|
| Usable energy | 11.5 kWh |
| Average power | ~34 kW |
| Peak power | ~88 kW (short climb) |
| Flight time | **~20 min** mixed |

---

## Procurement summary (Part 103)

| Line | Supplier | Qty | Est. |
|------|----------|-----|------|
| X-A12XL II-24S coaxial arm | T-MOTOR | 4 | ~$4,000 |
| 13.5 kWh 14S P60C pack | Danergy | 1 | ~$4,000–7,000 |
| Cube Orange | CubePilot | 1 | ~$1,500 |
| **Total propulsion** | | | **~$9,500–12,500** |

---

## What we dropped (45 min config)

| Removed | Reason |
|---------|--------|
| U15XL arms | Too heavy for 115 kg empty |
| 56 kWh dual packs | ~175 kg batteries alone |
| 310 kg MTOW | Exceeds Part 103 spirit and BRS sizing |

---

*Regenerate CAD: `bash scripts/build_all.sh` on aimainframe.*
