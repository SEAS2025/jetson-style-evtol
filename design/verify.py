"""Cross-check the solid model against the numbers printed on the drawing.

The general-arrangement sheet takes its dimension text straight from
`design.params`. This script proves the exported solid actually has those
dimensions, so the drawing cannot quietly start lying about the aircraft.
"""

from __future__ import annotations

import sys
from pathlib import Path

import trimesh

from design import params as P

ROOT = Path(__file__).resolve().parents[1]
STL = ROOT / "output" / "cad" / "solo1_frame_assembly.stl"
TOL_MM = 2.0


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    return mesh


def main() -> int:
    if not STL.exists():
        print(f"FAIL  missing {STL} — run design.frame_cad first")
        return 1

    mesh = load_mesh(STL)
    lo, hi = mesh.bounds
    dims = hi - lo

    checks = [
        ("overall length", float(dims[0]), P.LENGTH),
        ("overall width", float(dims[1]), P.WIDTH),
        ("overall height", float(dims[2]), P.HEIGHT),
        ("ground line at Z 0", float(lo[2]), 0.0),
        ("plan symmetry in Y", float(hi[1] + lo[1]), 0.0),
    ]

    failed = 0
    for name, got, want in checks:
        delta = got - want
        good = abs(delta) <= TOL_MM
        failed += 0 if good else 1
        print(f"  {'ok  ' if good else 'FAIL'}  {name:22s} "
              f"want {want:8.1f}  got {got:8.1f}  delta {delta:+7.2f}")

    for name, value in (("lateral tip gap", P.PROP_GAP_LATERAL),
                        ("longitudinal tip gap", P.PROP_GAP_LONGITUDINAL),
                        ("rotor-to-pod clearance", P.POD_TIP_CLEARANCE)):
        good = value > 0
        failed += 0 if good else 1
        print(f"  {'ok  ' if good else 'FAIL'}  {name:22s} {value:8.1f} mm")

    print("PASS — solid model matches the drawing" if not failed
          else f"{failed} check(s) failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
