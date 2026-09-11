"""Parametric aluminium spaceframe — tube sizes match the Aircraft Spruce catalog.

The solid model is built from the same stations and waterlines that the
general-arrangement drawing uses, so `solo1_general_arrangement.png` and
`solo1_frame_assembly.step` describe one aircraft rather than two.
"""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq

from design.params import (
    ARM_BOOM_OD_MM,
    ARM_DIHEDRAL_DEG,
    BAY_H,
    BAY_L,
    BAY_W,
    BOOM_LENGTH,
    BOOM_ROOT_X,
    BOOM_ROOT_Y,
    COCKPIT_W,
    CROSS_TUBE,
    HUB_D,
    HUB_H,
    MAIN_TUBE,
    MOTOR_STACK,
    POD_NOSE_X,
    POD_TAIL_X,
    PROP_DISK_R,
    ROLL_HOOP_D,
    ROTOR_STATIONS,
    SKID_OD,
    SKID_SPAN,
    SKID_TRACK,
    WL_BAY_BOTTOM,
    WL_BOOM_ROOT,
    WL_FLOOR,
    WL_HOOP_TOP,
    WL_ROTOR_LOWER,
    WL_ROTOR_UPPER,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "cad"


def _round_tube(length: float, od: float, wall: float | None = None) -> cq.Workplane:
    """Round tube extruded along +Z from the origin."""
    wp = cq.Workplane("XY").circle(od / 2)
    if wall and wall * 2 < od:
        wp = wp.circle(od / 2 - wall)
    return wp.extrude(length)


def _bar(length: float, w: float, h: float) -> cq.Workplane:
    """Square/rectangular bar running along +X from x = 0."""
    return cq.Workplane("XY").box(length, w, h).translate((length / 2.0, 0, 0))


def _boom(quadrant_x: float, quadrant_y: float) -> tuple[cq.Workplane, tuple[float, float, float]]:
    """One boom, plus the rotor axis it lands on.

    Built along +X, tilted up about Y by the dihedral, then swung about Z to
    the boom azimuth. Rotating about Y *before* Z is what keeps the dihedral
    in the boom's own plane instead of tilting it sideways.
    """
    root = (math.copysign(BOOM_ROOT_X, quadrant_x),
            math.copysign(BOOM_ROOT_Y, quadrant_y),
            WL_BOOM_ROOT)
    tip = (quadrant_x, quadrant_y)
    azimuth = math.degrees(math.atan2(tip[1] - root[1], tip[0] - root[0]))

    side = ARM_BOOM_OD_MM
    boom = _bar(BOOM_LENGTH, side, side)
    boom = boom.rotate((0, 0, 0), (0, 1, 0), -ARM_DIHEDRAL_DEG)
    boom = boom.rotate((0, 0, 0), (0, 0, 1), azimuth)
    return boom.translate(root), (tip[0], tip[1], WL_ROTOR_LOWER)


def build_frame() -> cq.Assembly:
    asm = cq.Assembly()

    # Keel rails (1 in square, Spruce 03-38900)
    keel_len = POD_NOSE_X - POD_TAIL_X
    for y in (-COCKPIT_W / 2 + MAIN_TUBE / 2, COCKPIT_W / 2 - MAIN_TUBE / 2):
        rail = _bar(keel_len, MAIN_TUBE, MAIN_TUBE).translate((POD_TAIL_X, y, WL_FLOOR))
        asm.add(rail, name=f"keel_{y:.0f}")

    # Transverse frames (3/4 in square, 03-00009)
    for x in (-BOOM_ROOT_X, 0.0, BOOM_ROOT_X):
        ring = (cq.Workplane("XY").box(CROSS_TUBE, COCKPIT_W, CROSS_TUBE)
                .translate((x, 0, WL_FLOOR)))
        asm.add(ring, name=f"frame_{x:.0f}")

    # Upper rails carrying the boom roots, and their posts
    for y in (-BOOM_ROOT_Y, BOOM_ROOT_Y):
        rail = _bar(2 * BOOM_ROOT_X, MAIN_TUBE, MAIN_TUBE).translate(
            (-BOOM_ROOT_X, y, WL_BOOM_ROOT))
        asm.add(rail, name=f"upper_rail_{y:.0f}")
        for x in (-BOOM_ROOT_X, BOOM_ROOT_X):
            post = _round_tube(WL_BOOM_ROOT - WL_FLOOR, MAIN_TUBE, wall=1.6)
            asm.add(post.translate((x, y, WL_FLOOR)), name=f"post_{x:.0f}_{y:.0f}")

    # Roll hoop (1-1/8 round, 03-00045): two posts and a swept crown, all in
    # the YZ plane at the hoop station. The crown sets overall height.
    hoop_r = COCKPIT_W / 2.0
    hoop_x = POD_TAIL_X + 140
    # WL_HOOP_TOP is the outer surface of the crown, so drop the centreline
    # by one tube radius.
    crown_z = WL_HOOP_TOP - hoop_r - ROLL_HOOP_D / 2.0
    post = (cq.Workplane("XY")
            .circle(ROLL_HOOP_D / 2).circle(ROLL_HOOP_D / 2 - 1.6)
            .extrude(crown_z - WL_FLOOR))
    for y in (-hoop_r, hoop_r):
        asm.add(post.translate((hoop_x, y, WL_FLOOR)), name=f"hoop_post_{y:.0f}")

    # Upper half of a tube torus about the X axis: the hoop's crown.
    axis = cq.Vector(1, 0, 0)
    crown = (cq.Solid.makeTorus(hoop_r, ROLL_HOOP_D / 2, cq.Vector(0, 0, 0), axis)
             .cut(cq.Solid.makeTorus(hoop_r, ROLL_HOOP_D / 2 - 1.6,
                                     cq.Vector(0, 0, 0), axis))
             .intersect(cq.Solid.makeBox(
                 4 * ROLL_HOOP_D, 4 * hoop_r, 2 * hoop_r,
                 cq.Vector(-2 * ROLL_HOOP_D, -2 * hoop_r, 0))))
    asm.add(cq.Workplane("XY").add(crown).translate((hoop_x, 0, crown_z)),
            name="hoop_crown")

    # Booms, coaxial motor stacks and prop-disk reference rings
    for i, (rx, ry) in enumerate(ROTOR_STATIONS):
        boom, axis = _boom(rx, ry)
        asm.add(boom, name=f"boom_{i}")

        mast = _round_tube(MOTOR_STACK + HUB_H, HUB_D, wall=3.0)
        asm.add(mast.translate((axis[0], axis[1], axis[2])), name=f"mast_{i}")

        for j, wl in enumerate((WL_ROTOR_LOWER, WL_ROTOR_UPPER)):
            disk = (cq.Workplane("XY")
                    .circle(PROP_DISK_R).circle(PROP_DISK_R - 4)
                    .extrude(6))
            asm.add(disk.translate((rx, ry, wl)), name=f"rotor_{i}_{j}")

    # Skid rails (0.930 round, 03-34400)
    for side in (-1, 1):
        skid = _round_tube(SKID_SPAN, SKID_OD, wall=1.6)
        skid = skid.rotate((0, 0, 0), (0, 1, 0), 90)
        asm.add(skid.translate((-SKID_SPAN / 2, side * SKID_TRACK / 2, SKID_OD / 2)),
                name=f"skid_{side}")

    # 13.5 kWh pack bay (Part 103 — pack <= 38 kg)
    tray = (cq.Workplane("XY").box(BAY_L, BAY_W, BAY_H)
            .translate((0, 0, WL_BAY_BOTTOM + BAY_H / 2)))
    asm.add(tray, name="battery_bay")

    return asm


def export_all() -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    asm = build_frame()
    written: list[Path] = []

    for name, kind in (("solo1_frame_assembly.step", "STEP"),
                       ("solo1_frame_assembly.stl", "STL")):
        path = OUT / name
        asm.save(str(path), exportType=kind)
        written.append(path)

    return written


if __name__ == "__main__":
    for p in export_all():
        print("wrote", p, p.stat().st_size)
