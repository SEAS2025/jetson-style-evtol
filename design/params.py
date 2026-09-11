"""SEAS Solo-1 — Part 103 ultralight coaxial octocopter (Jetson ONE class).

Coordinate system (right-handed, mm):
    +X  forward (nose)          X = 0 at the pod datum
    +Y  left (port)             Y = 0 on the plane of symmetry
    +Z  up                      Z = 0 at the skid ground line (WL0)

Rotor stations and waterlines are *derived* from the envelope and the
component stack so the drawings and the CAD cannot disagree. Nothing in
this module is a free-floating magic number that is only true on paper.
"""

from __future__ import annotations

import math

from design.spruce_catalog import TUBE_1RD, TUBE_1SQ, TUBE_34RD, TUBE_34SQ

# --- Target envelope (mm) — Jetson ONE class ---
LENGTH = 2700.0
WIDTH = 1600.0

# --- Rotors ---
PROP_DISK_D = 650.0
PROP_DISK_R = PROP_DISK_D / 2.0
MOTOR_STACK = 180.0            # vertical gap, lower rotor plane -> upper rotor plane
HUB_D = 90.0
HUB_H = 60.0                   # mast/hub above the upper rotor plane

# Rotor axes sit one prop radius inboard of the envelope, so the disk tips
# define LENGTH and WIDTH exactly.
ROTOR_X = LENGTH / 2.0 - PROP_DISK_R      # 1025
ROTOR_Y = WIDTH / 2.0 - PROP_DISK_R       # 475

#: (x, y) of the four coaxial rotor axes, nose-left pair first.
ROTOR_STATIONS: tuple[tuple[float, float], ...] = (
    (ROTOR_X, ROTOR_Y),
    (ROTOR_X, -ROTOR_Y),
    (-ROTOR_X, ROTOR_Y),
    (-ROTOR_X, -ROTOR_Y),
)

# Tip-to-tip clearance between adjacent disks (must stay positive).
PROP_GAP_LATERAL = 2.0 * ROTOR_Y - PROP_DISK_D        # 300
PROP_GAP_LONGITUDINAL = 2.0 * ROTOR_X - PROP_DISK_D   # 1400

# --- Cockpit pod ---
COCKPIT_W = 520.0
COCKPIT_L = 680.0
COCKPIT_H = 420.0
POD_NOSE_X = 700.0             # forward face of the pod fairing
POD_TAIL_X = -520.0            # aft face

# --- Tubing (Aircraft Spruce 6061-T6) ---
MAIN_TUBE = TUBE_1SQ["od_mm"]
CROSS_TUBE = TUBE_34SQ["od_mm"]
ROLL_HOOP_D = TUBE_1RD["od_mm"]
SKID_OD = TUBE_34RD["od_mm"]
ARM_BOOM_OD_MM = 50.0          # T-MOTOR X-A12XL arm tube

SKID_SPAN = 900.0              # fore/aft length of each skid rail
SKID_TRACK = 680.0             # lateral distance between the two skid rails

# --- Waterlines (Z, mm above ground line) ---
WL_GROUND = 0.0
WL_SKID_TOP = SKID_OD
WL_BAY_BOTTOM = 120.0
BAY_L, BAY_W, BAY_H = 600.0, 350.0, 180.0     # 13.5 kWh Danergy pack envelope
WL_BAY_TOP = WL_BAY_BOTTOM + BAY_H            # 300
WL_FLOOR = WL_BAY_TOP                         # cockpit floor sits on the pack
WL_SEAT = WL_FLOOR + 40.0
WL_BOOM_ROOT = 700.0                          # boom pickup on the upper truss
WL_HOOP_TOP = 1120.0                          # roll structure = tallest point

# --- Booms ---
ARM_DIHEDRAL_DEG = 8.0
ARM_ELEVATION_DEG = ARM_DIHEDRAL_DEG          # back-compat alias

#: Boom root pickups, at the four upper corners of the cockpit truss.
BOOM_ROOT_X = COCKPIT_L / 2.0                 # 340
BOOM_ROOT_Y = COCKPIT_W / 2.0                 # 260

_run_x = ROTOR_X - BOOM_ROOT_X                # 685
_run_y = ROTOR_Y - BOOM_ROOT_Y                # 215
BOOM_RUN = math.hypot(_run_x, _run_y)         # 718 — horizontal projection
BOOM_AZIMUTH_DEG = math.degrees(math.atan2(_run_y, _run_x))   # 17.4 deg off centerline
BOOM_RISE = BOOM_RUN * math.tan(math.radians(ARM_DIHEDRAL_DEG))
BOOM_LENGTH = math.hypot(BOOM_RUN, BOOM_RISE)  # true cut length
ARM_SPAN = BOOM_RUN                            # back-compat alias

WL_ROTOR_LOWER = WL_BOOM_ROOT + BOOM_RISE     # ~801
WL_ROTOR_UPPER = WL_ROTOR_LOWER + MOTOR_STACK  # ~981
WL_MAST_TOP = WL_ROTOR_UPPER + HUB_H

HEIGHT = max(WL_HOOP_TOP, WL_MAST_TOP)        # derived overall height

FOLDED_WIDTH = 2.0 * BOOM_ROOT_Y + PROP_DISK_D  # booms folded aft against the pod

# --- FAA Part 103 (14 CFR 103.1) ---
PART103 = True
PART103_EMPTY_MAX_KG = 115.0   # 254 lb
PART103_SPEED_MAX_KMH = 102.0  # 55 kt ~ 102 km/h (software limit)

# --- Mission ---
FLIGHT_TIME_MIN = 20           # realistic at Part 103 mass budget
BATTERY_KWH_NOMINAL = 13.5
BATTERY_KWH_USABLE = 11.5      # ~85% DoD
AVG_POWER_KW = BATTERY_KWH_USABLE / (FLIGHT_TIME_MIN / 60.0)  # ~34 kW
PEAK_POWER_KW = 88.0

MTOW_KG = 210.0
EMPTY_KG = 115.0               # hard cap incl. batteries
PILOT_MAX_KG = 95.0            # 210 - 115
BATTERY_MASS_KG = 38.0         # ~13.5 kWh high-discharge pack

MOTORS = 8
ARMS = 4

#: Rotor disk loading — the number that explains the ~20 min endurance.
DISK_AREA_M2 = MOTORS * math.pi * (PROP_DISK_R / 1000.0) ** 2
DISK_LOADING_KG_M2 = MTOW_KG / DISK_AREA_M2

# Frozen vendor SKUs — see docs/PROPULSION.md
PROPULSION_KIT = "T-MOTOR X-A12XL II-24S Coaxial"
PROPULSION_QTY = 4
BATTERY_VENDOR = "Danergy custom Molicel P60C"
BATTERY_MODULES = 1
BATTERY_VOLTAGE_S = 14           # 14S nominal (~50 V class, Jetson-like)

# Guard rails: fail loudly if someone edits the envelope into nonsense.
assert PROP_GAP_LATERAL > 0, "lateral rotor disks overlap"
assert PROP_GAP_LONGITUDINAL > 0, "longitudinal rotor disks overlap"
assert abs((2 * ROTOR_X + PROP_DISK_D) - LENGTH) < 1e-6, "plan length != envelope"
assert abs((2 * ROTOR_Y + PROP_DISK_D) - WIDTH) < 1e-6, "plan width != envelope"


def _pod_clearance_mm() -> float:
    """Smallest gap between any rotor disk edge and the cockpit pod box."""
    gaps = []
    for rx, ry in ROTOR_STATIONS:
        dx = max(POD_TAIL_X - rx, 0.0, rx - POD_NOSE_X)
        dy = max(-COCKPIT_W / 2.0 - ry, 0.0, ry - COCKPIT_W / 2.0)
        gaps.append(math.hypot(dx, dy) - PROP_DISK_R)
    return min(gaps)


POD_TIP_CLEARANCE = _pod_clearance_mm()

assert POD_TIP_CLEARANCE > 0, "rotor disk strikes the cockpit pod"
