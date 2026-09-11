"""How much lift a lifting-body cab and stub airfoils actually produce.

Part 103 caps level flight at 55 kt and lift goes as V squared, so the honest
question is not "does the body make lift" but "how much of the 210 kg does it
carry at the only speeds we are allowed to fly".

Planforms are laid out in real plan coordinates so two things get checked
rather than assumed: whether a surface fits inside the existing envelope, and
how much of it actually sits under a rotor disk where it costs download in
hover.

Run:  PYTHONPATH=. .venv/bin/python -m design.aero_cruise
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from design import params as P

RHO = 1.225          # kg/m^3, ISA sea level
G = 9.80665
KT_TO_MS = 0.514444


@dataclass(frozen=True)
class Panel:
    """A rectangular planform patch in aircraft plan coordinates (mm)."""
    x0: float
    x1: float
    y0: float
    y1: float

    @property
    def area_m2(self) -> float:
        return abs(self.x1 - self.x0) * abs(self.y1 - self.y0) / 1e6


@dataclass(frozen=True)
class Surface:
    name: str
    panels: tuple[Panel, ...]
    cl_cruise: float      # trimmed CL at small positive incidence
    cd0: float            # profile drag on its own area
    mass_kg: float        # installed mass penalty

    @property
    def area_m2(self) -> float:
        return sum(p.area_m2 for p in self.panels)


# The cab: a sailplane-style lifting body. It does make lift, but a fuselage
# is not a wing, so CL stays low.
CAB = Surface(
    "lifting-body cab",
    panels=(Panel(P.POD_TAIL_X, P.POD_NOSE_X, -P.COCKPIT_W / 2, P.COCKPIT_W / 2),),
    cl_cruise=0.35, cd0=0.060, mass_kg=0.0,
)

# Stub airfoils, sized to stop at the existing 1600 mm width rather than
# sticking out past it. Chord set by what fits between the fore and aft disks.
STUB_CHORD = 450.0
STUB_X0 = -STUB_CHORD / 2
STUB_Y_IN = P.COCKPIT_W / 2
STUB_Y_OUT = P.WIDTH / 2
STUBS = Surface(
    "stub airfoils (2)",
    panels=(Panel(STUB_X0, STUB_X0 + STUB_CHORD, STUB_Y_IN, STUB_Y_OUT),
            Panel(STUB_X0, STUB_X0 + STUB_CHORD, -STUB_Y_OUT, -STUB_Y_IN)),
    cl_cruise=0.80, cd0=0.012, mass_kg=9.0,
)


def q(v_ms: float) -> float:
    return 0.5 * RHO * v_ms * v_ms


def lift_n(s: Surface, v_ms: float) -> float:
    return q(v_ms) * s.area_m2 * s.cl_cruise


def drag_n(s: Surface, v_ms: float) -> float:
    return q(v_ms) * s.area_m2 * s.cd0


def _under_disk(x: float, y: float) -> bool:
    return any(math.hypot(x - rx, y - ry) <= P.PROP_DISK_R
               for rx, ry in P.ROTOR_STATIONS)


def shaded_fraction(s: Surface, step: float = 10.0) -> float:
    """Fraction of a surface's planform that lies under a rotor disk."""
    total = inside = 0
    for p in s.panels:
        x = min(p.x0, p.x1) + step / 2
        while x < max(p.x0, p.x1):
            y = min(p.y0, p.y1) + step / 2
            while y < max(p.y0, p.y1):
                total += 1
                if _under_disk(x, y):
                    inside += 1
                y += step
            x += step
    return inside / total if total else 0.0


def fits_envelope(s: Surface) -> tuple[bool, float]:
    """Does the surface stay inside the published width?"""
    half = max(max(abs(p.y0), abs(p.y1)) for p in s.panels)
    return (2 * half) <= P.WIDTH + 1e-6, 2 * half


def main() -> None:
    weight_n = P.MTOW_KG * G
    print(f"MTOW {P.MTOW_KG:.0f} kg = {weight_n:.0f} N")
    print(f"Part 103 ceiling {P.PART103_SPEED_MAX_KMH:.0f} km/h = 55 kt")
    print(f"cab planform  {CAB.area_m2:.2f} m^2")
    print(f"stub planform {STUBS.area_m2:.2f} m^2 "
          f"({STUB_CHORD:.0f} mm chord, {STUB_Y_OUT - STUB_Y_IN:.0f} mm span per side)\n")

    print(f"{'speed':>17} | {'cab lift':>16} | {'stub lift':>16} | {'combined':>17}")
    print(f"{'':>17} | {'N':>7} {'% W':>8} | {'N':>7} {'% W':>8} | {'N':>7} {'% W':>8}")
    print("-" * 76)
    for kt in (20, 30, 40, 50, 55):
        v = kt * KT_TO_MS
        lc, ls = lift_n(CAB, v), lift_n(STUBS, v)
        tot = lc + ls
        print(f"{kt:>3} kt {v:>5.1f} m/s | {lc:>7.0f} {100*lc/weight_n:>7.1f}% | "
              f"{ls:>7.0f} {100*ls/weight_n:>7.1f}% | "
              f"{tot:>7.0f} {100*tot/weight_n:>7.1f}%")

    v55 = 55 * KT_TO_MS
    print("\n--- at the 55 kt ceiling ---")
    for s in (CAB, STUBS):
        print(f"  {s.name:22s} lift {lift_n(s, v55):6.0f} N "
              f"({lift_n(s, v55)/G:5.1f} kg)   drag {drag_n(s, v55):5.0f} N")
    tot_kg = (lift_n(CAB, v55) + lift_n(STUBS, v55)) / G
    print(f"  {'combined':22s} lift {tot_kg:5.1f} kg of {P.MTOW_KG:.0f} kg "
          f"= {100*tot_kg/P.MTOW_KG:.0f}% offloaded")

    print("\n--- does it fit the envelope? ---")
    for s in (CAB, STUBS):
        ok, width = fits_envelope(s)
        print(f"  {s.name:22s} spans {width:6.0f} mm of {P.WIDTH:.0f} mm  "
              f"{'OK' if ok else 'EXCEEDS WIDTH'}")

    print("\n--- hover download: how much sits under a rotor disk ---")
    for s in (CAB, STUBS):
        f = shaded_fraction(s)
        print(f"  {s.name:22s} {100*f:5.1f}% shaded "
              f"({f * s.area_m2:.2f} m^2 of {s.area_m2:.2f} m^2)")

    print("\n--- mass budget ---")
    print(f"  empty weight is already at the Part 103 cap of "
          f"{P.PART103_EMPTY_MAX_KG:.0f} kg")
    print(f"  stubs add an estimated {STUBS.mass_kg:.0f} kg installed, which has "
          f"to come out of airframe, pack or pilot")
    print(f"  stubs return {lift_n(STUBS, v55)/G/STUBS.mass_kg:.1f} kg of lift "
          f"per kg of wing, but only at the 55 kt ceiling")


if __name__ == "__main__":
    main()
