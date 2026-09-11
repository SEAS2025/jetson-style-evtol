# SEAS Solo-1 — Bill of Materials

Concept single-seat coaxial octocopter, Jetson ONE–class envelope. **Primary airframe, hardware, harness, and parachute from [Aircraft Spruce & Specialty](https://www.aircraftspruce.com).** Propulsion and avionics are listed separately (not Spruce catalog).

Target: **FAA Part 103** — **≤115 kg (254 lb) empty** incl. batteries, **≤55 kt**, single seat, **~20 min** flight, **210 kg MTOW** max.

---

## A. Airframe tubing (6061-T6) — Aircraft Spruce

Order by foot: add dash length to part number (e.g. `03-38900-6` = 6 ft).

| Qty | Spruce P/N | Description | Used for | Est. length |
|-----|------------|-------------|----------|-------------|
| 4 | **03-38900** | 1 × 1 × 0.065 sq tube | Keel rails, arm booms | 6 ft each |
| 6 | **03-00009** | 3/4 × 3/4 × 0.049 sq tube | Cross members, battery tray, gusset stubs | 4 ft each |
| 2 | **03-00045** | 1-1/8 OD × 0.065 round tube | Roll hoop (cut/weld or splice) | 6 ft |
| 2 | **03-34400** | 0.930 OD × 0.065 round tube | Skid rails | 4 ft |

Links:
- [03-38900](https://www.aircraftspruce.com/catalog/pnpages/03-38900.php)
- [03-00009](https://www.aircraftspruce.com/catalog/pnpages/03-00009.php)
- [Square tubing index](https://www.aircraftspruce.com/catalog/mepages/alumtubing-sq.php)
- [Round tubing index](https://www.aircraftspruce.com/catalog/mepages/alumtubing-rd.php)

---

## B. Hardware — Aircraft Spruce

| Qty | Spruce P/N | Description | Application |
|-----|------------|-------------|-------------|
| 16 | **05-17037** | McFarlane MCS1105-3 rod end, 10-32 ext | Motor mount / arm fold fittings |
| 8 | **04-03454** | Heim HF-3M rod end (surplus) | Alternate / jury strut |
| 120 | **AN3-6A** … **AN3-10A** | AN3 bolts (pick grip per joint) | Gussets, brackets |
| 120 | **MS21042-3** | Stop nut 10-32 | With AN3 |
| 240 | **AN960-10** | Flat washer for AN3 | Under bolt head + nut |
| 200 | **AN470AD4-5** | 1/8 in universal rivet (example) | Gusset plates — match length to grip |
| 8 | **AN4-6A** | 1/4-28 bolt | Harness mounts, parachute brackets |
| 8 | **MS21042-4** | Stop nut 1/4-28 | With AN4 |
| 16 | **AN960-416** | Washer for AN4 | Harness / chute |

Selectors:
- [AN bolts](https://www.aircraftspruce.com/catalog/stpages/anbolts.php)
- [MS21042 nuts](https://www.aircraftspruce.com/catalog/pnpages/MS21042-3.php)
- [AN960 washers](https://www.aircraftspruce.com/catalog/hapages/flatwashers.php)
- [Solid rivets AN470](https://www.aircraftspruce.com/catalog/mepages/solidrivets.php)

---

## C. Safety — Aircraft Spruce

| Qty | Spruce P/N | Description | Notes |
|-----|------------|-------------|-------|
| 1 | **13-01300** | Style No. 5 seat belt / harness set | 2 in webbing; 1/4 in attach bolt |
| 1 | **13-20942** | BRS Top VLS Genesis ultralight chute | Confirm weight band with BRS |
| 1 | — | Full-face helmet (pilot supplied) | Open cockpit |

- [13-01300 harness](https://www.aircraftspruce.com/catalog/appages/seatbelt5.php)
- [13-20942 parachute](https://www.aircraftspruce.com/catalog/pnpages/13-20942.php)

---

## D. Electrical (Spruce wire + external packs)

| Qty | Spruce P/N | Description | Notes |
|-----|------------|-------------|-------|
| 50 ft | **MIL-W-22759/32-12** | Wire 12 AWG (example) | Motor feeds — order exact AWG from [wire section](https://www.aircraftspruce.com/catalog/mepages/wire.php) |
| 100 ft | **MIL-W-22759/32-20** | Wire 20 AWG | Signal / CAN |
| 1 | **11-02600** (series) | Adel clamps / lacing | Secure harness to frame |
| 1 | — | Danergy ~13.5 kWh 14S pack | ≤38 kg — see `PROPULSION.md` |

---

## E. Propulsion (not Aircraft Spruce)

**Full sourcing guide:** `docs/PROPULSION.md`

### Frozen Part 103 configuration

| Qty | Supplier | Part | Description | Link |
|-----|----------|------|-------------|------|
| 4 | **T-MOTOR** | **X-A12XL II-24S** | Coaxial arm: 2× motor + 2× 120A ESC + props | [shop.tmotor.com](https://shop.tmotor.com/products/x-a12xl-v2-24s-coaxial-uav-propulsion-system) |
| 1 | **Danergy** | Custom **13.5 kWh 14S P60C** | ≤38 kg, CAN BMS | [danenergy.com](https://www.danenergy.com/catalog/lithium-ion-battery-packs/) |
| 1 | **CubePilot** | Cube Orange | ArduPilot, **55 kt** speed limit | [cubepilot.org](https://cubepilot.org) |
| 1 | **Molicel** | INR-21700-P60C | Cell spec for pack builder | [molicel.com](https://www.molicel.com/inr-21700-p60c/) |

| Qty | Item | Spec |
|-----|------|------|
| 1 | 4-axis stick | Thrust / yaw / pitch / roll |
| 1 | Speed governor | Software ≤ **55 kt** (Part 103) |

See **`docs/PROPULSION.md`** for mass budget and thrust-margin notes.

---

## F. Consumables & shop

| Item | Source |
|------|--------|
| 6061 gusset sheet 0.063 in | Spruce aluminum sheet section |
| 4043 TIG rod | Spruce welding |
| Epoxy (carbon knee braces) | Spruce composites |
| Cherry/Avdel rivets if used | Spruce rivet section |

---

## Weight summary (Part 103 — 254 lb empty cap)

| Component | kg |
|-----------|-----|
| Airframe (aluminum) | 28 |
| Harness + chute | 16 |
| Battery (~13.5 kWh P60C) | 38 |
| 4× X-A12XL arm kits | 20 |
| Avionics + wiring | 5 |
| Props / guards (in kits) | 8 |
| **Empty (with batteries)** | **115** (max) |
| Pilot (max) | 95 |
| **MTOW** | **210** |

---

*Verify every Spruce P/N, length suffix, and price at order time. This is a concept homebuilt — not a type-certified design.*
