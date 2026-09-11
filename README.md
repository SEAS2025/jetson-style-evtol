# SEAS Solo-1

Single-seat electric octocopter targeting **FAA 14 CFR Part 103** (≤254 lb / 115 kg
empty, ≤55 kt level speed, one occupant), ~20 min endurance, 210 kg MTOW.
Airframe from **Aircraft Spruce** carbon tube; propulsion **T-MOTOR X-A12XL**
with a 13.5 kWh pack.

> Research and design study, not a flight-cleared design. Nothing here has been
> structurally tested. Read `docs/` before drawing conclusions.

## How this repo is wired

`design/params.py` is the single source of truth. The general-arrangement
drawing takes its dimension text from it and the CAD takes its geometry from
it, so the drawing cannot drift away from the model. `design/verify.py` then
loads the exported STL and asserts its bounding box back against those
parameters — if geometry and drawing ever disagree, the build fails.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
bash scripts/build_all.sh
```

| Output | What it is |
| --- | --- |
| `output/views/solo1_general_arrangement.png` | Third-angle GA drawing, all views at 1:20 |
| `output/cad/solo1_frame_assembly.{step,stl}` | Spaceframe |
| `output/cad/cab_shell.{step,stl}` | Printed cockpit cab |
| `docs/BOM.md` | Aircraft Spruce part numbers |
| `docs/PROPULSION.md` | Mass budget and motor selection |

## The printed cab

A one-piece-per-segment PETG shell that replaces both the pod skin and the
roll hoop. It is **not primary structure**: Aircraft Spruce carbon tubes slide
into moulded interfaces and carry every flight load. PETG interlayer adhesion
is about 39% of in-plane strength, and EASA CM-S-008 treats polymer additive
manufacturing as suitable only for low-criticality parts, so the print is an
aerodynamic fairing plus seat support.

Shape follows a **Schempp-Hirth** high-performance sailplane forward fuselage:
fine nose entry, egg-shaped sections with the wide lobe down, maximum width at
the shoulders, contracting tailcone. Sections are held inside the 0.72–0.78
width-to-height band measured across the Discus a/b, Ventus-2a and a scaled
Radespiel ASW 19 survey. Real sailplane fuselages are taller than wide, which
is the opposite of most fairing intuition.

Run the pre-loft checks before touching geometry:

```bash
PYTHONPATH=. .venv/bin/python -m design.cab_check   # pilot fit, rotor clearance, bond, print volume
PYTHONPATH=. .venv/bin/python -m design.cab_cad     # loft the shell (~15 s for the loft alone)
```

### Things that are easy to get wrong

- **Aircraft Spruce indexes its carbon tube table by *inside* diameter, not
  outside.** A "1 inch" tube is a 1.000″ bore with a 0.120″ wall, so the real
  OD is 1.240″. Sockets modelled at 1.000″ would fit nothing. `SPRUCE_TUBES`
  derives OD as ID + 2×wall for this reason.
- **Do not infill the cab.** It encloses ~510 litres, so even 9% gyroid
  through that volume is ~58 kg of PETG — heavier than the entire airframe
  allowance. It prints as a hollow shell at zero infill, with solid material
  only in socket bosses and flange pads. Skin-only mass is 9.15 kg.
- **Tube interfaces are through-bores, not opposing blind sockets.** A rigid
  tube cannot enter two sockets that face each other, and the requirement is
  to slide members in after printing.
- **Loft sections must be single spline edges.** A smooth loft through
  polyline wires makes OCC solve a surface per edge per section and
  effectively never returns at this section count.
- **The Tronxy VEHO 1000-20 is 1000 × 1000 × 2000 mm** — the "-20" suffix is
  the Z height, not the model year. Z is capped to 600 mm per part here by
  choice, because that axis has the worst tramming drift and this machine
  family has a poor reliability record.

## Current state

Passing: rotor-disk clearance along the whole cab, reclined pilot fit to the
MIL-STD-1472G 50 mm floor, section ratio against published sailplane sections,
12-part segmentation inside the build volume, and bonded socket engagement
sized for the CS-22.561 9 g case with Hysol EA 9430.

Known and deliberate: fineness ratio is 3.19 against a Discus-class 9.5, and
the maximum section sits at 64% of length against Radespiel's measured 24%.
Both are artefacts of a truncated pod with no tailboom. The aft body will
separate without a tail fairing. Printed seams also stand proud of the 0.75 mm
laminar trip height, so treat the surface as fully turbulent.

### Next

1. Split the lofted shell into the 12 print parts and export a plate layout.
2. `docs/CAB.md` — print settings, tube BOM, assembly and bonding sequence.
3. Regenerate the GA drawing: the cab crown at z 1150 replaces the roll hoop,
   taking overall height 1120 → 1150 and length 2700 → 2750.

## Design parameters

Airframe: `design/params.py`. Cab: `design/cab_params.py`. Tube catalog:
`design/spruce_catalog.py`. Edit, re-run the checks, then rebuild.
