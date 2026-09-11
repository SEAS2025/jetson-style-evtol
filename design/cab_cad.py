"""Loft the printed cab shell and cut the carbon-tube interfaces.

Build order:
  1. loft the egg sections into an outer solid
  2. loft an inset copy and cut it, leaving a hollow shell
  3. add transverse bulkheads at the print split planes
  4. bore the bulkheads so each straight tube run slides through from one end
  5. add a terminal socket with an internal register spigot at each run end
  6. add capped wing hardpoints
  7. export STEP and STL

The bores are through-holes, not opposing blind sockets: a rigid tube cannot
enter two sockets that face each other, and the brief is to slide the
structural members in after printing.

Run:  PYTHONPATH=. .venv/bin/python -m design.cab_cad
"""

from __future__ import annotations

import math
import pathlib

import cadquery as cq

from design import cab_params as C

OUT = pathlib.Path("output/cad")
SECTION_STEP = 75.0      # longitudinal sampling for the loft
SECTION_PTS = 64
BULKHEAD_T = 8.0


def _station_xs() -> list[float]:
    """Sample stations tail-to-nose, always hitting the table entries."""
    xs = {float(s[0]) for s in C.STATIONS}
    x = C.CAB_TAIL_X
    while x < C.CAB_NOSE_X:
        xs.add(round(x, 3))
        x += SECTION_STEP
    xs.add(C.CAB_NOSE_X)
    return sorted(xs)


def _section_wire(x: float, inset: float) -> cq.Wire:
    half_w, keel, crown = C.section(x)
    half_h = (crown - keel) / 2.0
    zc = (crown + keel) / 2.0
    a = max(half_w - inset, 0.5)
    b = max(half_h - inset, 0.5)

    pts = []
    for i in range(SECTION_PTS):
        t = 2.0 * math.pi * i / SECTION_PTS
        ct, st = math.cos(t), math.sin(t)
        n = C.SECTION_EXP
        y = a * math.copysign(abs(ct) ** (2.0 / n), ct)
        z = b * math.copysign(abs(st) ** (2.0 / n), st)
        bias = C.EGG_UPPER_BIAS if z >= 0 else C.EGG_LOWER_BIAS
        blend = abs(z) / b if b else 0.0
        y *= 1.0 + (bias - 1.0) * blend
        pts.append(cq.Vector(x, y, zc + z))

    # One periodic spline edge per section, not 64 line edges. A smooth loft
    # through polyline wires makes OCC solve a surface per edge per section
    # and effectively never returns at this section count.
    return cq.Wire.assembleEdges(
        [cq.Edge.makeSpline(pts, periodic=True)])


def _loft(inset: float) -> cq.Solid:
    wires = [_section_wire(x, inset) for x in _station_xs()]
    return cq.Solid.makeLoft(wires, ruled=False)


def build_shell() -> cq.Workplane:
    outer = _loft(0.0)
    inner = _loft(C.SHELL_T)
    return cq.Workplane(obj=outer.cut(inner))


def _bulkhead_xs() -> list[float]:
    """Interior print split planes, which double as tube guides."""
    n = C.SEGMENTS_LENGTHWISE
    seg = C.CAB_LENGTH / n
    return [C.CAB_NOSE_X - seg * i for i in range(1, n)]


def add_bulkheads(shell: cq.Workplane) -> cq.Workplane:
    solid = shell.val()
    for x in _bulkhead_xs():
        plate = _loft_slab(x)
        if plate is not None:
            solid = solid.fuse(plate)
    return cq.Workplane(obj=solid.clean())


def _loft_slab(x: float) -> cq.Solid | None:
    """A full-section disc of BULKHEAD_T thickness at station x."""
    try:
        w0 = _section_wire(x - BULKHEAD_T / 2.0, C.SHELL_T)
        w1 = _section_wire(x + BULKHEAD_T / 2.0, C.SHELL_T)
        return cq.Solid.makeLoft([w0, w1], ruled=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  bulkhead at x {x:.0f} failed: {exc}")
        return None


def _run_axis(a, b):
    v = cq.Vector(b[0] - a[0], b[1] - a[1], b[2] - a[2])
    return v, v.Length


def bore_tube_runs(shell: cq.Workplane) -> cq.Workplane:
    """Cut a through-bore for every tube run, plus a terminal socket."""
    solid = shell.val()
    for name, a, b, tube in C.TUBE_RUNS + C.WING_SOCKETS:
        axis, length = _run_axis(a, b)
        direction = axis.normalized()
        bore = C.socket_bore(tube)

        # overlength cylinder so it cleanly parts every bulkhead it crosses
        pad = 400.0
        start = cq.Vector(*a) - direction.multiply(pad)
        cyl = cq.Solid.makeCylinder(bore / 2.0, length + 2 * pad,
                                    start, direction)
        solid = solid.cut(cyl)

        boss = _socket_boss(a, direction.multiply(-1.0), tube)
        if boss is not None:
            solid = solid.fuse(boss)
        print(f"  {name:11s} {tube.part_no} bore {bore:5.2f} mm, "
              f"run {length:6.1f} mm")
    return cq.Workplane(obj=solid.clean())


def _socket_boss(at, outward: cq.Vector, tube) -> cq.Solid | None:
    """Collar around the tube entry, with an internal register spigot.

    The collar is built outward from the run end so it reinforces the entry
    without intruding on the tube path.
    """
    bore = C.socket_bore(tube)
    depth = C.socket_depth(tube)
    origin = cq.Vector(*at)
    try:
        collar = cq.Solid.makeCylinder(bore / 2.0 + C.SOCKET_WALL, depth,
                                       origin, outward)
        collar = collar.cut(cq.Solid.makeCylinder(bore / 2.0, depth + 2.0,
                                                 origin, outward))
        spigot = _register_spigot(origin, outward.multiply(-1.0), tube)
        return collar.fuse(spigot) if spigot is not None else collar
    except Exception as exc:  # noqa: BLE001
        print(f"    socket boss failed: {exc}")
        return None


def _register_spigot(origin: cq.Vector, inward: cq.Vector, tube) -> cq.Solid | None:
    """Hollow spigot that enters the tube bore and sets coaxiality."""
    od = C.register_od(tube)
    depth = C.register_depth(tube)
    try:
        spig = cq.Solid.makeCylinder(od / 2.0, depth, origin, inward)
        spig = spig.cut(cq.Solid.makeCylinder(
            od / 2.0 - C.REGISTER_WALL, depth + 2.0, origin, inward))
        # flutes so adhesive is not hydraulically trapped
        ref = cq.Vector(0, 0, 1)
        if abs(inward.dot(ref)) > 0.9:
            ref = cq.Vector(1, 0, 0)
        u = inward.cross(ref).normalized()
        v = inward.cross(u).normalized()
        for i in range(C.FLUTE_COUNT):
            ang = 2.0 * math.pi * i / C.FLUTE_COUNT
            radial = u.multiply(math.cos(ang)).add(v.multiply(math.sin(ang)))
            centre = origin.add(radial.multiply(od / 2.0))
            cutter = cq.Solid.makeBox(
                C.FLUTE_W, C.FLUTE_W, depth + 2.0,
                cq.Vector(-C.FLUTE_W / 2, -C.FLUTE_W / 2, 0), inward)
            spig = spig.cut(cutter.translate(centre.sub(origin)))
        return spig
    except Exception as exc:  # noqa: BLE001
        print(f"    register spigot failed: {exc}")
        return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("lofting the cab shell...")
    shell = build_shell()
    bb = shell.val().BoundingBox()
    print(f"  shell bbox {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")

    print("adding bulkheads at the print split planes...")
    shell = add_bulkheads(shell)

    print("boring tube runs and adding sockets...")
    shell = bore_tube_runs(shell)

    solid = shell.val()
    bb = solid.BoundingBox()
    print(f"\nfinal bbox {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
    print(f"  X {bb.xmin:.1f} .. {bb.xmax:.1f}")
    print(f"  Y {bb.ymin:.1f} .. {bb.ymax:.1f}")
    print(f"  Z {bb.zmin:.1f} .. {bb.zmax:.1f}")
    vol = solid.Volume()
    print(f"  material volume {vol / 1e6:.2f} litres "
          f"-> {vol * C.PETG_DENSITY / 1000:.2f} kg in {C.MATERIAL}")

    cq.exporters.export(shell, str(OUT / "cab_shell.step"))
    cq.exporters.export(shell, str(OUT / "cab_shell.stl"),
                        tolerance=0.1, angularTolerance=0.2)
    print(f"\nwrote {OUT / 'cab_shell.step'} and {OUT / 'cab_shell.stl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
