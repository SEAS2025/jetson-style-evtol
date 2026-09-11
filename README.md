# SEAS Solo-1

Single-seat coaxial octocopter — **FAA Part 103** (≤254 lb empty, ≤55 kt), **~20 min**, 210 kg MTOW. **Airframe = Aircraft Spruce.** **Propulsion = T-MOTOR X-A12XL + 13.5 kWh Danergy pack.**

## Build on aimainframe (RTX 3070 + Blender)

```bash
cd ~/Projects/jetson-style-evtol
bash scripts/build_all.sh
```

Outputs:
- `output/cad/` — STEP + STL spaceframe
- `output/views/` — top, side, front, iso orthographic PNGs
- `docs/BOM.md` — Spruce part numbers
- `docs/CONSTRUCTION.md` — assembly sequence

## Design parameters

Edit `design/params.py` and `design/spruce_catalog.py`, then rebuild.
