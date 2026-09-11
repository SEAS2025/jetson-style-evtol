# SEAS Solo-1 — Construction Instructions

Coaxial octocopter, **FAA Part 103** ultralight (**≤115 kg empty**, **~20 min**). **All primary structure uses Aircraft Spruce 6061-T6 tube and AN/MS hardware** (see `BOM.md`). Propulsion: **4× T-MOTOR X-A12XL** + **13.5 kWh Danergy pack** (`PROPULSION.md`).

## Tools required

- Tube notcher or milling fixture for 1 in / 3/4 in square tube
- TIG welder (4043 filler) or bolted gusset construction
- Rivet gun (AN470) or AN3 bolted gussets
- Drill press, deburr, cleco kit
- Torque wrench for AN3/AN4
- Blender/CAD prints in `output/views/` for alignment

## Phase 1 — Cockpit safety cell

1. **Cut keel rails** from **03-38900** (1 × 1 × 0.065): two lengths ~1.5 m, parallel, spaced **COCKPIT_W** (520 mm) apart.
2. **Cross members** from **03-00009**: three rings at fore, mid, aft cockpit — square-cut, fish-mouth or gusset into keels.
3. **Roll hoop** from **03-00045**: bend to arc (≈ 600 mm ID), weld or sleeve-splice at base; mount to forward cross member with **AN4-6A** + **AN960-416** + **MS21042-4**.
4. Mount **13-01300** harness to hoop and aft cross member (1/4 in attach bolts per Spruce).
5. Install **13-20942** BRS top mount per BRS template — forward of pilot, clear prop disk.

## Phase 2 — Arm hardpoints

1. Fabricate four arm sockets from 1 in sq tube stubs welded to keels at **45°, 135°, 225°, 315°**.
2. **Arm booms** (03-38900): length **ARM_SPAN** (~720 mm), slight dihedral (**8°**).
3. At inboard end: **05-17037** rod end (MCS1105-3) for fold hinge — pin with **AN3** bolt + **MS21042-3** + **AN960-10**.
4. At outboard end: motor plate (aluminum gusset 0.063 sheet from Spruce) — two coax stacks separated **180 mm** vertically.

## Phase 3 — Motor / prop stack (per arm)

1. Upper and lower motor mounts tied with 3/4 in cross tube (**03-00009**).
2. Prop guard ring: carbon or aluminum — **650 mm** disk reference (see CAD).
3. Route **MIL-W-22759** motor leads along arm with Adel clamps; strain relief at hinge.

## Phase 4 — Landing gear

1. **Skids** from **03-34400**: two rails, **SKID_SPAN** 900 mm, splayed 15°.
2. Attach to keel with bolted gussets (AN3) — replaceable wear pads at ground contact.

## Phase 5 — Battery tray (Part 103 weight critical)

1. Single bay from **03-38900** + **03-00009** — ~**600 × 350 × 180 mm** (one **≤38 kg** Danergy 13.5 kWh module).
2. **Weigh empty aircraft** on scales after every structural change — must stay **≤ 115 kg (254 lb)** including battery.
3. Quick-release: 4× **AN4-6A** + **MS21042-4**; Anderson **SB50** or per Danergy spec.
4. CG: pack centered slightly forward of arm hub.

## Phase 6 — Systems

1. Flight computer and bus above battery tray; segregate power and signal harnesses.
2. 4-axis stick on right; arm/disarm interlock on left.
3. Ground test: motor sync, tilt stand, tethered hover before manned flight.

## Phase 7 — Fold (road trailer)

1. Arms fold upward using rod-end hinges; target folded width **980 mm** (props removed or hinged guards).
2. Pin each arm with **AN3** quick pins (Spruce pin section) for transport.

## Drawings

| View | File |
|------|------|
| Top | `output/views/solo1_top.png` |
| Side | `output/views/solo1_side.png` |
| Front | `output/views/solo1_front.png` |
| Isometric | `output/views/solo1_iso.png` |
| CAD STEP | `output/cad/solo1_frame_assembly.step` |
| CAD STL | `output/cad/solo1_frame_assembly.stl` |

Regenerate: `bash scripts/build_all.sh`

## Regulatory note

**14 CFR Part 103:** 254 lb empty, 55 kt max, single seat, day VFR. Set ArduPilot speed limit to **102 km/h**. Not FAA type certified. Weigh before flight. Thrust-test each arm at **≥52.5 kg** before manned ops (see `PROPULSION.md`).
