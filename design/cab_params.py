"""Printed cockpit cab — parametric definition.

Shape language follows a Schempp-Hirth forward fuselage: fine nose entry,
egg-shaped cross-section with the wide lobe down, maximum width at the
pilot's shoulders, a canopy crown that encloses the head so the shell itself
is the roll structure, and a contracting tailcone.

The shell is NOT primary structure. Aircraft Spruce carbon tubes slide into
moulded sockets and carry every flight load; the print is an aerodynamic
fairing plus seat support. Prusa's own data puts PETG interlayer adhesion at
~39% of in-plane strength, and EASA CM-S-008 treats polymer AM as suitable
only for low-criticality parts. See docs/CAB.md.

Coordinates match design.params: +X forward, +Y left, +Z up, Z 0 at the skid
ground line.
"""

from __future__ import annotations

import math

INCH = 25.4

# --------------------------------------------------------------------------
# Printer envelope — Tronxy VEHO 1000-20, confirmed
# Bed is 1000 x 1000 mm, usable Z is 2000 mm. The "-NN" suffix is the Z
# height, so 1000-16 is 1600 mm and 1000-20 is 2000 mm.
# --------------------------------------------------------------------------
BUILD_X = 1000.0
BUILD_Y = 1000.0
BUILD_Z = 2000.0
BUILD_MARGIN = 25.0          # brim/skirt and bed-levelling edge error

#: Z is deliberately not used to anything like its full height: it is the
#: axis with the worst tramming drift and the longest exposure to a
#: mid-print fault on this machine.
MAX_PART_Z = 600.0

USABLE_X = BUILD_X - 2 * BUILD_MARGIN
USABLE_Y = BUILD_Y - 2 * BUILD_MARGIN
USABLE_Z = min(BUILD_Z - 2 * BUILD_MARGIN, MAX_PART_Z)

# --------------------------------------------------------------------------
# Aircraft Spruce carbon tube — CRITICAL: the catalog table is indexed by
# INSIDE diameter, not outside. A "1 inch" tube is 1.000" bore with a 0.120"
# wall, so OD is 1.240". Sockets modelled at 1.000" would fit nothing.
# Verified against the published 0.79 lb/ft for the 3" tube.
# Family page: aircraftspruce.com/catalog/cmpages/fortertubing.php
# --------------------------------------------------------------------------
class SpruceTube:
    """A real catalog tube. OD is derived as ID + 2 x wall."""

    __slots__ = ("part_no", "id_in", "wall_in", "usd_per_ft", "lb_per_ft", "note")

    def __init__(self, part_no: str, id_in: float, wall_in: float,
                 usd_per_ft: float, lb_per_ft: float, note: str = "") -> None:
        self.part_no = part_no
        self.id_in = id_in
        self.wall_in = wall_in
        self.usd_per_ft = usd_per_ft
        self.lb_per_ft = lb_per_ft
        self.note = note

    @property
    def od_mm(self) -> float:
        return (self.id_in + 2 * self.wall_in) * INCH

    @property
    def id_mm(self) -> float:
        return self.id_in * INCH

    @property
    def wall_mm(self) -> float:
        return self.wall_in * INCH

    def __repr__(self) -> str:
        return (f"{self.part_no} ID {self.id_in:.3f}in wall {self.wall_in:.3f}in "
                f"-> OD {self.od_mm:.2f}mm")


#: Only sizes orderable on the US web table.
SPRUCE_TUBES: dict[str, SpruceTube] = {
    "03-00171": SpruceTube("03-00171", 0.500, 0.100, 45.80, 0.127, "skip: dear and weak"),
    "03-00172": SpruceTube("03-00172", 0.750, 0.100, 45.80, 0.179, "diagonals and bracing"),
    "03-00173": SpruceTube("03-00173", 1.000, 0.120, 35.80, 0.284, "cheapest per ft, backbone"),
    "03-00174": SpruceTube("03-00174", 1.250, 0.120, 51.50, 0.347, "skip: dearer and weaker than 1.5"),
    "03-00175": SpruceTube("03-00175", 1.500, 0.120, 41.50, 0.410, "highest-load members"),
    "03-00176": SpruceTube("03-00176", 1.750, 0.120, 56.50, 0.474, ""),
    "03-00177": SpruceTube("03-00177", 2.000, 0.120, 46.50, 0.537, "single large spine only"),
    "03-00178": SpruceTube("03-00178", 2.500, 0.120, 72.00, 0.663, ""),
}

TUBE_KEEL = SPRUCE_TUBES["03-00175"]     # OD 44.20 mm — keel longerons
TUBE_FRAME = SPRUCE_TUBES["03-00173"]    # OD 31.50 mm — frames, boom pickups
TUBE_DIAG = SPRUCE_TUBES["03-00172"]     # OD 24.13 mm — diagonals

#: Aircraft Spruce publishes NO dimensional tolerance for this tubing, and
#: filament-wound tube typically holds ID well and OD loosely. So the socket
#: is deliberately generous and the joint relies on a thick bonded gap
#: rather than a slip fit.
SOCKET_CLEARANCE = 0.80      # radial, 1.6 mm on diameter
SOCKET_WALL = 6.0            # printed material around each socket

#: Engagement is set by bending, not shear. Shear alone needs only ~20 mm,
#: but a tube in a socket reacts moment as a couple across the engagement,
#: so the usual 3x-diameter rule governs and keeps bearing stress on the
#: printed bore low.
SOCKET_DEPTH_DIAMETERS = 3.0

# --- internal register spigot ------------------------------------------------
# The socket bore is deliberately loose because OD is the uncontrolled
# dimension. A concentric spigot entering the tube BORE then sets coaxial
# alignment, because the bore is the dimension filament winding actually
# holds. The spigot locates; it carries no design load.
REGISTER_CLEARANCE = 0.30    # radial, against the controlled bore
REGISTER_DEPTH_DIAMETERS = 1.0
REGISTER_WALL = 4.0          # printed wall of the spigot itself

#: Without an escape path the adhesive hydraulic-locks as the tube slides
#: over the spigot and the joint bottoms out dry. Flutes down the spigot and
#: a bleed hole at the socket root give it somewhere to go.
FLUTE_COUNT = 4
FLUTE_W = 5.0
FLUTE_DEPTH = 1.5
BLEED_HOLE_D = 5.0


def socket_bore(tube: "SpruceTube") -> float:
    """Loose bore that accepts the uncontrolled tube OD."""
    return tube.od_mm + 2.0 * SOCKET_CLEARANCE


def socket_depth(tube: "SpruceTube") -> float:
    return SOCKET_DEPTH_DIAMETERS * tube.od_mm


def register_od(tube: "SpruceTube") -> float:
    """Spigot OD, sized off the controlled bore."""
    return tube.id_mm - 2.0 * REGISTER_CLEARANCE


def register_depth(tube: "SpruceTube") -> float:
    return REGISTER_DEPTH_DIAMETERS * tube.id_mm

# --------------------------------------------------------------------------
# Adhesive — Loctite/Hysol EA 9430, Aircraft Spruce P/N 02-18600
# Chosen because Henkel qualifies it to a 0.100 in (2.54 mm) bondline, which
# is what a printed socket's layer texture and shrinkage actually delivers.
# Size bonds off the FRP number, not the headline aluminium number.
# --------------------------------------------------------------------------
ADHESIVE_PN = "02-18600"
ADHESIVE_NAME = "Loctite/Hysol EA 9430"
ADHESIVE_LAP_SHEAR_FRP_PSI = 1400.0     # 77 F, composite substrate
ADHESIVE_LAP_SHEAR_140F_PSI = 1700.0    # aluminium at 140 F, for derating
ADHESIVE_MAX_BONDLINE_MM = 0.100 * INCH
ADHESIVE_DERATE_HOT = 0.36              # retained fraction at 140 F
BOND_SAFETY_FACTOR = 3.0

# --------------------------------------------------------------------------
# Shell and print process — PETG on an open-frame machine
# --------------------------------------------------------------------------
MATERIAL = "PETG"
PETG_DENSITY = 1.27e-3       # g/mm^3, Prusament TDS
NOZZLE = 0.6                 # stock; 0.8 preferred if available
EXTRUSION_W = NOZZLE * 1.1
PERIMETERS = 3
SHELL_T = PERIMETERS * EXTRUSION_W       # 1.98 mm at a 0.6 nozzle

# --------------------------------------------------------------------------
# Print segmentation. Twelve parts: 6 lengthwise segments, each split on the
# centreline, every half laid on its flat cut face. Chosen over 6 larger
# parts because the VEHO 1000 family has a poor reliability record and a
# lost 13 h print costs far less than a lost 25 h one.
# --------------------------------------------------------------------------
SEGMENTS_LENGTHWISE = 6
HALVES = 2
PART_COUNT = SEGMENTS_LENGTHWISE * HALVES

#: Realistic large-format PETG throughput at a 0.6 nozzle and 0.3 mm layers,
#: on a perimeter-dominated part with almost no infill.
PRINT_RATE_G_PER_H = 60.0
MAX_PRINT_HOURS = 18.0

#: Printed as a HOLLOW SHELL with zero infill. This is not a detail: the cab
#: encloses about 510 litres, so even 9% gyroid through that volume would be
#: ~46 litres of PETG, around 58 kg. Infill belongs only in local solid
#: regions such as socket bosses and flanges.
INFILL = 0.0
SOLID_REGION_INFILL = 0.35   # inside socket bosses and flange pads only
FLANGE_W = 30.0              # bolted flange at each print split
FLANGE_T = 6.0
LAP_OVERLAP = 22.0           # bonded lap at each seam, ~8x skin

#: Laminar flow on a sailplane forward fuselage is tripped by any protrusion
#: over 0.75 mm (Boermans & Terleth). A printed seam cannot meet that, so
#: seams must be filled and faired, and this is recorded as a known limit.
LAMINAR_TRIP_HEIGHT = 0.75

# --------------------------------------------------------------------------
# Reclined pilot. Clearance floor is MIL-STD-1472G 5.6.2.2: 50 mm minimum
# between any body part and any hard surface.
# --------------------------------------------------------------------------
PILOT_CLEARANCE = 50.0
PILOT_MASS_MAX_KG = 110.0       # Schempp-Hirth single-seat seat-load ceiling
PILOT_STATURE_MAX = 1850.0

#: Heels sit at x 820, not further forward: the forward rotor disks cap the
#: shell half-width near x 940, so the pedals cannot go there. Everything
#: forward of the pedals becomes nose cone, trim ballast and crush structure,
#: which is exactly how a Discus uses that volume.
PILOT_HEEL = (820.0, 0.0, 375.0)
PILOT_KNEE = (520.0, 0.0, 470.0)
PILOT_HIP = (120.0, 0.0, 390.0)
PILOT_SHOULDER = (-250.0, 0.0, 890.0)
PILOT_HEAD_C = (-330.0, 0.0, 995.0)
PILOT_HEAD_R = 110.0

PILOT_FOOT_HALF_W = 110.0       # both feet on pedals, near the centreline
PILOT_KNEE_HALF_W = 150.0
PILOT_HIP_HALF_W = 210.0
PILOT_SHOULDER_HALF_W = 235.0   # 470 mm biacromial plus clothing

SEAT_BACK_ANGLE_DEG = 30.0      # F-16 datum, best-validated reclined figure
SEAT_PAN_MIN_W = 460.0          # MIL-STD-1472G minimum
SEAT_PAN_OPT_W = 610.0          # MIL-STD-1472G optimum

# --------------------------------------------------------------------------
# Fuselage station table: (x, half_width, keel_z, crown_z) in mm.
# Width-to-height ratio is held in the 0.72-0.78 band measured across the
# Discus a/b, Ventus-2a and Radespiel ASW 19 sections. Sections are taller
# than wide, which is the opposite of most fairing intuition.
# --------------------------------------------------------------------------
STATIONS: tuple[tuple[float, float, float, float], ...] = (
    (1400.0,  14.0, 452.0, 468.0),    # nose tip
    (1300.0,  46.0, 424.0, 505.0),
    (1180.0,  78.0, 396.0, 548.0),
    (1060.0, 104.0, 370.0, 585.0),    # threads between the forward disks
    (940.0,  134.0, 330.0, 620.0),
    (820.0,  168.0, 313.0, 655.0),    # rudder pedals / pilot heels
    (650.0,  208.0, 304.0, 702.0),
    (500.0,  240.0, 300.0, 745.0),
    (350.0,  266.0, 298.0, 815.0),
    (200.0,  288.0, 296.0, 905.0),
    (50.0,   302.0, 296.0, 1015.0),
    (-100.0, 310.0, 298.0, 1108.0),   # maximum section, 620 x 810
    (-250.0, 306.0, 304.0, 1158.0),   # shoulders
    (-400.0, 292.0, 314.0, 1168.0),   # canopy crown over the head
    (-550.0, 266.0, 328.0, 1138.0),
    (-700.0, 230.0, 346.0, 1068.0),
    (-850.0, 188.0, 368.0, 966.0),
    (-950.0, 150.0, 384.0, 892.0),    # tailcone cut, aft of the boom pickups
)

CAB_NOSE_X = STATIONS[0][0]
CAB_TAIL_X = STATIONS[-1][0]
CAB_LENGTH = CAB_NOSE_X - CAB_TAIL_X

#: Egg-curve asymmetry: real sailplane sections are Hügelschäffer curves with
#: the wide lobe low, for hips and legs, narrowing at the shoulders and
#: canopy. This is a controlled approximation of that form, not the
#: Hügelschäffer construction itself.
EGG_LOWER_BIAS = 1.06        # lower lobe width multiplier
EGG_UPPER_BIAS = 0.88        # upper lobe width multiplier
SECTION_EXP = 2.3            # 2 = ellipse, higher = fuller shoulders

#: Published reference sections, for validation in cab_check.
REFERENCE_SECTIONS = (
    ("Discus a / Ventus-2a", 540.0, 750.0),
    ("Discus b / Ventus-2b", 620.0, 810.0),
    ("Thomas design constraint", 600.0, 800.0),
    ("Radespiel ASW 19, scaled", 642.0, 822.0),
)
#: Radespiel's measured maximum section sits 23.6% of fuselage length aft of
#: the nose. A truncated pod cannot match that; recorded so the gap is
#: explicit rather than forgotten.
REFERENCE_MAX_SECTION_FRAC = 0.236
REFERENCE_FINENESS = 9.5


def rotor_half_width_limit(x: float) -> float | None:
    """Largest half-width at station x that still clears every rotor disk."""
    from design.params import PROP_DISK_R, ROTOR_STATIONS

    worst: float | None = None
    for rx, ry in ROTOR_STATIONS:
        dx = abs(x - rx)
        if dx >= PROP_DISK_R:
            continue
        inboard = abs(ry) - math.sqrt(PROP_DISK_R ** 2 - dx ** 2)
        worst = inboard if worst is None else min(worst, inboard)
    return None if worst is None else worst - ROTOR_MARGIN


ROTOR_MARGIN = 25.0          # air gap held between shell and any rotor disk


def _clamp(x: float, half_w: float) -> float:
    limit = rotor_half_width_limit(x)
    return half_w if limit is None else min(half_w, limit)


def section(x: float) -> tuple[float, float, float]:
    """Interpolated (half_width, keel_z, crown_z) at station x.

    Half-width is clamped so the shell cannot intrude on a rotor disk: the
    station table is a target, the rotor geometry is the authority.
    """
    pts = STATIONS
    if x >= pts[0][0]:
        return _clamp(x, pts[0][1]), pts[0][2], pts[0][3]
    if x <= pts[-1][0]:
        return _clamp(x, pts[-1][1]), pts[-1][2], pts[-1][3]
    for (x0, w0, k0, c0), (x1, w1, k1, c1) in zip(pts, pts[1:]):
        if x1 <= x <= x0:
            t = (x - x0) / (x1 - x0)
            return (_clamp(x, w0 + (w1 - w0) * t),
                    k0 + (k1 - k0) * t,
                    c0 + (c1 - c0) * t)
    raise ValueError(x)


def egg_outline(half_w: float, half_h: float, n: float = SECTION_EXP,
                count: int = 96) -> list[tuple[float, float]]:
    """Egg-shaped section: superellipse with the wide lobe biased low."""
    out: list[tuple[float, float]] = []
    for i in range(count):
        t = 2.0 * math.pi * i / count
        ct, st = math.cos(t), math.sin(t)
        y = half_w * math.copysign(abs(ct) ** (2.0 / n), ct)
        z = half_h * math.copysign(abs(st) ** (2.0 / n), st)
        bias = EGG_UPPER_BIAS if z >= 0 else EGG_LOWER_BIAS
        blend = abs(z) / half_h if half_h else 0.0
        out.append((y * (1.0 + (bias - 1.0) * blend), z))
    return out


def section_points(x: float, inset: float = 0.0) -> list[tuple[float, float]]:
    """Cross-section outline at station x, optionally inset for the bore."""
    half_w, keel, crown = section(x)
    half_h = (crown - keel) / 2.0
    zc = (crown + keel) / 2.0
    a = max(half_w - inset, 0.4)
    b = max(half_h - inset, 0.4)
    return [(y, zc + z) for y, z in egg_outline(a, b)]


def max_section_x() -> float:
    return max(STATIONS, key=lambda s: s[1])[0]


def fineness_ratio() -> float:
    """Hoerner convention for a non-circular body: f = 2L / (h + w)."""
    w = max(s[1] for s in STATIONS) * 2.0
    h = max(c - k for _, _, k, c in STATIONS)
    return 2.0 * CAB_LENGTH / (w + h)


def required_bond_length(tube: SpruceTube, load_n: float) -> float:
    """Socket engagement needed to carry load_n in shear, hot and derated."""
    psi_to_mpa = 0.00689476
    tau = (ADHESIVE_LAP_SHEAR_FRP_PSI * psi_to_mpa
           * ADHESIVE_DERATE_HOT / BOND_SAFETY_FACTOR)
    circumference = math.pi * tube.od_mm
    return load_n / (tau * circumference)


# --------------------------------------------------------------------------
# Structural tube runs: (name, start, end, tube)
# --------------------------------------------------------------------------
KEEL_Y = 205.0
KEEL_Z = 350.0
UPPER_Y = 250.0
UPPER_Z = 700.0

TUBE_RUNS = (
    ("keel_port", (1000.0, KEEL_Y, KEEL_Z), (-900.0, KEEL_Y, KEEL_Z), TUBE_KEEL),
    ("keel_stbd", (1000.0, -KEEL_Y, KEEL_Z), (-900.0, -KEEL_Y, KEEL_Z), TUBE_KEEL),
    ("upper_port", (340.0, UPPER_Y, UPPER_Z), (-340.0, UPPER_Y, UPPER_Z), TUBE_FRAME),
    ("upper_stbd", (340.0, -UPPER_Y, UPPER_Z), (-340.0, -UPPER_Y, UPPER_Z), TUBE_FRAME),
    ("frame_fwd", (340.0, 280.0, KEEL_Z), (340.0, -280.0, KEEL_Z), TUBE_FRAME),
    ("frame_mid", (0.0, 300.0, KEEL_Z), (0.0, -300.0, KEEL_Z), TUBE_FRAME),
    ("frame_aft", (-340.0, 290.0, KEEL_Z), (-340.0, -290.0, KEEL_Z), TUBE_FRAME),
    ("diag_port", (340.0, UPPER_Y, UPPER_Z), (-40.0, KEEL_Y, KEEL_Z), TUBE_DIAG),
    ("diag_stbd", (340.0, -UPPER_Y, UPPER_Z), (-40.0, -KEEL_Y, KEEL_Z), TUBE_DIAG),
)

#: Wing hardpoints, moulded now and capped until wings are fitted.
WING_SOCKETS = (
    ("wing_port", (0.0, 240.0, 560.0), (0.0, 900.0, 560.0), TUBE_FRAME),
    ("wing_stbd", (0.0, -240.0, 560.0), (0.0, -900.0, 560.0), TUBE_FRAME),
)
