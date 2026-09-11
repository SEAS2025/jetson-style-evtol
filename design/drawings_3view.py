"""SEAS Solo-1 general-arrangement drawing — third-angle 3-view.

Every view is plotted at one shared, *preferred* scale (1:10, 1:20, 1:25 ...)
and the views are projection-aligned: the plan sits directly above the side
elevation and shares its X limits, the front elevation sits beside the side
elevation and shares its Z limits. A millimetre is therefore the same length
everywhere on the sheet and the views line up the way a draughtsman expects.

Shapes and dimension text are both generated from `design.params`, so a
callout cannot drift away from the geometry it is measuring.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Circle, Polygon, Rectangle

from design import params as P

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "views"

# --- Drafting style: ink on paper, ISO-ish line weights ---
INK = "#12161c"
DIM = "#1c4e80"
CENTER = "#8060a8"
PHANTOM = "#98a2ae"
HIDDEN = "#6f7885"
ROTOR_CLR = "#a8481c"
FILL_STRUCT = "#e2e8ef"
FILL_BAY = "#c9dcf0"
FILL_PANEL = "#f6f8fb"
PAPER = "#ffffff"

LW_VISIBLE = 1.6
LW_THIN = 0.8
LW_DIM = 0.7

ARROW = dict(arrowstyle="-|>,head_width=0.15,head_length=0.42", lw=LW_DIM, color=DIM)

SHEET_W, SHEET_H = 15.5, 11.6      # A3-ish landscape, inches
MARGIN = 0.40
GAP_MM = 220.0                     # gutter between views, model mm
PREFERRED_SCALES = (5, 10, 15, 20, 25, 30, 40, 50, 75, 100)

HOOP_X = P.POD_TAIL_X + 140.0      # roll hoop plane, just aft of the pilot's head


# ----------------------------------------------------------------------------
# drafting primitives
# ----------------------------------------------------------------------------
def _dim_h(ax, x1, x2, y_line, y_from, text, *, fontsize=8.4):
    """Horizontal dimension with witness lines and paired inward arrowheads."""
    for x in (x1, x2):
        ax.plot([x, x], [y_from, y_line], color=DIM, lw=LW_DIM, zorder=6)
    mid = (x1 + x2) / 2.0
    ax.annotate("", xy=(x1, y_line), xytext=(mid, y_line), arrowprops=ARROW, zorder=6)
    ax.annotate("", xy=(x2, y_line), xytext=(mid, y_line), arrowprops=ARROW, zorder=6)
    ax.text(mid, y_line, text, ha="center", va="center", color=DIM,
            fontsize=fontsize, bbox=dict(fc=PAPER, ec="none", pad=1.8), zorder=7)


def _dim_v(ax, y1, y2, x_line, x_from, text, *, fontsize=8.4):
    """Vertical dimension with witness lines and paired inward arrowheads."""
    for y in (y1, y2):
        ax.plot([x_from, x_line], [y, y], color=DIM, lw=LW_DIM, zorder=6)
    mid = (y1 + y2) / 2.0
    ax.annotate("", xy=(x_line, y1), xytext=(x_line, mid), arrowprops=ARROW, zorder=6)
    ax.annotate("", xy=(x_line, y2), xytext=(x_line, mid), arrowprops=ARROW, zorder=6)
    ax.text(x_line, mid, text, ha="center", va="center", color=DIM, rotation=90,
            fontsize=fontsize, bbox=dict(fc=PAPER, ec="none", pad=1.8), zorder=7)


def _balloon(ax, n, at, to):
    """Numbered item balloon with a leader to the feature."""
    ax.annotate("", xy=at, xytext=to,
                arrowprops=dict(arrowstyle="-", lw=LW_DIM, color=INK,
                                shrinkA=0, shrinkB=9), zorder=8)
    ax.add_patch(Circle(to, 62, fc=PAPER, ec=INK, lw=0.9, zorder=9))
    ax.text(to[0], to[1], str(n), ha="center", va="center", fontsize=7.8,
            fontweight="bold", color=INK, zorder=10)


def _centerline(ax, p1, p2):
    ax.add_line(Line2D([p1[0], p2[0]], [p1[1], p2[1]], color=CENTER, lw=0.7,
                       ls=(0, (16, 4, 2, 4)), zorder=3))


def _axis_cross(ax, x, y, r):
    _centerline(ax, (x - r, y), (x + r, y))
    _centerline(ax, (x, y - r), (x, y + r))


def _ground(ax, x0, x1, z=0.0):
    ax.plot([x0, x1], [z, z], color=INK, lw=2.2, zorder=5)
    n, step = 48, (x1 - x0) / 48.0
    for i in range(n):
        gx = x0 + i * step
        ax.plot([gx, gx - step * 0.85], [z, z - step * 0.85],
                color=INK, lw=0.5, zorder=4)


def _rotor_disk_edge(ax, cx, cz, *, horiz_axis="x"):
    """Coaxial pair seen edge-on: two rotor planes plus the mast."""
    ax.plot([cx, cx], [P.WL_ROTOR_LOWER, P.WL_MAST_TOP],
            color=INK, lw=2.6, solid_capstyle="round", zorder=7)
    for wl in (P.WL_ROTOR_LOWER, P.WL_ROTOR_UPPER):
        ax.plot([cx - P.PROP_DISK_R, cx + P.PROP_DISK_R], [wl, wl],
                color=PHANTOM, lw=6.0, alpha=0.35, zorder=5)
        ax.plot([cx - P.PROP_DISK_R, cx + P.PROP_DISK_R], [wl, wl],
                color=INK, lw=1.9, solid_capstyle="butt", zorder=6)
    ax.add_patch(Rectangle((cx - P.HUB_D / 2, P.WL_ROTOR_LOWER),
                           P.HUB_D, P.MOTOR_STACK, fc=FILL_STRUCT, ec=INK,
                           lw=LW_THIN, zorder=6))


def _boom_polygon(root, tip, width):
    dx, dy = tip[0] - root[0], tip[1] - root[1]
    n = math.hypot(dx, dy)
    ox, oy = -dy / n * width / 2.0, dx / n * width / 2.0
    return [(root[0] + ox, root[1] + oy), (tip[0] + ox, tip[1] + oy),
            (tip[0] - ox, tip[1] - oy), (root[0] - ox, root[1] - oy)]


def _view_axes(fig, rect, xlim, ylim, label, subtitle):
    ax = fig.add_axes(rect)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0.0, 1.012, f"{label}  \u2014  {subtitle}", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=12.0, fontweight="bold", color=INK)
    return ax


# ----------------------------------------------------------------------------
# PLAN VIEW
# ----------------------------------------------------------------------------
def draw_plan(ax):
    hw = P.COCKPIT_W / 2.0

    for rx, ry in P.ROTOR_STATIONS:
        ax.add_patch(Circle((rx, ry), P.PROP_DISK_R, fill=False, ec=PHANTOM,
                            lw=1.0, ls=(0, (10, 4)), zorder=3))
        _axis_cross(ax, rx, ry, P.PROP_DISK_R * 1.1)

        # diagonally opposite pairs counter-rotate for yaw authority
        cw = (rx > 0) == (ry > 0)
        r = P.PROP_DISK_R * 0.70
        t1, t2 = (200, 330) if cw else (30, 160)
        ax.add_patch(Arc((rx, ry), 2 * r, 2 * r, theta1=t1, theta2=t2,
                         color=ROTOR_CLR, lw=1.2, zorder=6))
        ta = math.radians(t2 if cw else t1)
        tip = (rx + math.cos(ta) * r, ry + math.sin(ta) * r)
        head = math.radians(t2 + 16 if cw else t1 - 16)
        ax.annotate("", xy=(rx + math.cos(head) * r, ry + math.sin(head) * r),
                    xytext=tip,
                    arrowprops=dict(arrowstyle="-|>,head_width=0.18,head_length=0.5",
                                    lw=1.2, color=ROTOR_CLR), zorder=6)
        ax.text(rx, ry + (r + 70) * (1 if ry > 0 else -1), "CW" if cw else "CCW",
                ha="center", va="center", fontsize=7.4, color=ROTOR_CLR, zorder=7)

        ax.add_patch(Circle((rx, ry), P.HUB_D / 2, fc=INK, ec=INK, zorder=8))
        root = (math.copysign(P.BOOM_ROOT_X, rx), math.copysign(P.BOOM_ROOT_Y, ry))
        ax.add_patch(Polygon(_boom_polygon(root, (rx, ry), P.ARM_BOOM_OD_MM),
                             closed=True, fc=FILL_STRUCT, ec=INK,
                             lw=LW_VISIBLE, zorder=5))

    # cockpit pod
    pod = [(P.POD_NOSE_X, 0.0), (P.POD_NOSE_X - 130, hw * 0.70), (320, hw),
           (-300, hw), (P.POD_TAIL_X, hw * 0.60), (P.POD_TAIL_X, -hw * 0.60),
           (-300, -hw), (320, -hw), (P.POD_NOSE_X - 130, -hw * 0.70)]
    ax.add_patch(Polygon(pod, closed=True, fc=FILL_STRUCT, ec=INK,
                         lw=LW_VISIBLE, zorder=4))

    rail_y = hw - P.MAIN_TUBE / 2.0
    for sy in (-1, 1):
        ax.plot([-460, 600], [sy * rail_y, sy * rail_y],
                color=INK, lw=LW_THIN, zorder=6)
    for fx in (-P.BOOM_ROOT_X, 0.0, P.BOOM_ROOT_X):
        ax.plot([fx, fx], [-rail_y, rail_y], color=INK, lw=LW_THIN, zorder=6)

    # roll hoop lies in the YZ plane, so it projects as a straight line here
    ax.plot([HOOP_X, HOOP_X], [-hw, hw], color=INK, lw=2.4, zorder=7)

    ax.add_patch(Rectangle((-P.BAY_L / 2, -P.BAY_W / 2), P.BAY_L, P.BAY_W,
                           fc="none", ec=HIDDEN, lw=1.0, ls=(0, (7, 3)), zorder=6))

    for sy in (-1, 1):
        ax.plot([-P.SKID_SPAN / 2, P.SKID_SPAN / 2],
                [sy * P.SKID_TRACK / 2] * 2, color=INK, lw=2.4,
                solid_capstyle="round", zorder=5)

    _centerline(ax, (-P.LENGTH / 2 - 150, 0), (P.LENGTH / 2 + 150, 0))
    _centerline(ax, (0, -P.WIDTH / 2 - 150), (0, P.WIDTH / 2 + 90))

    # dimensions
    _dim_h(ax, -P.LENGTH / 2, P.LENGTH / 2, -1000, -P.WIDTH / 2,
           f"{P.LENGTH:.0f}   OVERALL LENGTH")
    _dim_h(ax, -P.ROTOR_X, P.ROTOR_X, -880, -P.ROTOR_Y - P.PROP_DISK_R,
           f"{2 * P.ROTOR_X:.0f}   ROTOR BASE")
    _dim_v(ax, -P.WIDTH / 2, P.WIDTH / 2, -1620, -P.LENGTH / 2,
           f"{P.WIDTH:.0f}   OVERALL WIDTH")
    _dim_v(ax, -P.ROTOR_Y, P.ROTOR_Y, -1430, -P.ROTOR_X,
           f"{2 * P.ROTOR_Y:.0f}   ROTOR TRACK")
    # lateral tip gap, dimensioned where the gap actually is
    _dim_v(ax, -P.ROTOR_Y + P.PROP_DISK_R, P.ROTOR_Y - P.PROP_DISK_R,
           P.ROTOR_X, P.ROTOR_X - 165, f"{P.PROP_GAP_LATERAL:.0f} TIP GAP",
           fontsize=7.4)

    # rotor disk diameter, dimensioned across the disk it belongs to
    rx, ry = -P.ROTOR_X, P.ROTOR_Y
    a = math.radians(45)
    ax.annotate("", xy=(rx - math.cos(a) * P.PROP_DISK_R, ry - math.sin(a) * P.PROP_DISK_R),
                xytext=(rx + math.cos(a) * P.PROP_DISK_R, ry + math.sin(a) * P.PROP_DISK_R),
                arrowprops=dict(arrowstyle="<|-|>,head_width=0.15,head_length=0.42",
                                lw=LW_DIM, color=DIM), zorder=7)
    ax.text(rx, ry, f"\u2300{P.PROP_DISK_D:.0f}", ha="center", va="center",
            fontsize=8.4, color=DIM, bbox=dict(fc=PAPER, ec="none", pad=1.8), zorder=8)

    # boom azimuth
    ax.add_patch(Arc((P.BOOM_ROOT_X, P.BOOM_ROOT_Y), 900, 900, theta1=0,
                     theta2=P.BOOM_AZIMUTH_DEG, color=DIM, lw=LW_DIM, zorder=6))
    _centerline(ax, (P.BOOM_ROOT_X - 40, P.BOOM_ROOT_Y), (P.BOOM_ROOT_X + 560, P.BOOM_ROOT_Y))
    ax.text(P.BOOM_ROOT_X + 500, P.BOOM_ROOT_Y + 92, f"{P.BOOM_AZIMUTH_DEG:.1f}\u00b0",
            fontsize=8.0, color=DIM, zorder=7)

    # balloons live in the clear bands between the fore and aft rotor disks
    _balloon(ax, 1, (P.ROTOR_X, P.ROTOR_Y), (620, 690))
    _balloon(ax, 2, ((P.BOOM_ROOT_X + P.ROTOR_X) / 2, -(P.BOOM_ROOT_Y + P.ROTOR_Y) / 2),
             (330, -660))
    _balloon(ax, 3, (140, hw), (170, 690))
    _balloon(ax, 4, (-P.BAY_L / 2 + 80, -P.BAY_W / 2), (-140, -660))
    _balloon(ax, 5, (HOOP_X, hw * 0.45), (-330, 690))
    _balloon(ax, 6, (-P.SKID_SPAN / 2 + 140, -P.SKID_TRACK / 2), (-600, -660))


# ----------------------------------------------------------------------------
# SIDE ELEVATION
# ----------------------------------------------------------------------------
POD_TOP_EDGE = ((P.POD_TAIL_X, 640.0), (-300.0, 660.0), (150.0, 500.0),
                (430.0, 462.0), (P.POD_NOSE_X, 420.0))


def _pod_top_z(x: float) -> float:
    """Z of the cockpit tub's upper edge at station x."""
    for (x0, z0), (x1, z1) in zip(POD_TOP_EDGE, POD_TOP_EDGE[1:]):
        if x0 <= x <= x1:
            return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
    return P.WL_FLOOR


def _pilot_side(ax):
    """Reclined 50th-percentile pilot, phantom outline — sets the cabin scale."""
    kw = dict(color=HIDDEN, lw=0.9, ls=(0, (6, 4)), zorder=7, alpha=0.85)
    ax.plot([120, -250], [390, 900], **kw)                   # torso
    ax.plot([120, 470, 660], [390, 470, 345], **kw)          # thigh + shin
    ax.plot([-250, 60], [900, 560], **kw)                    # arm to grip
    ax.add_patch(Circle((-320, 1000), 105, fill=False, ec=HIDDEN, lw=0.9,
                        ls=(0, (6, 4)), alpha=0.85, zorder=7))
    ax.text(-60, 1080, "PILOT REF (RECLINED)", fontsize=7.0, color=HIDDEN,
            ha="left", va="center", zorder=7)


def draw_side(ax):
    _ground(ax, -P.LENGTH / 2 - 80, P.LENGTH / 2 + 80)

    ax.plot([-P.SKID_SPAN / 2, P.SKID_SPAN / 2], [P.SKID_OD / 2] * 2,
            color=INK, lw=2.8, solid_capstyle="round", zorder=6)
    for sx in (-250, 250):
        ax.plot([sx, sx], [P.SKID_OD, P.WL_BAY_BOTTOM], color=INK, lw=LW_VISIBLE, zorder=6)

    ax.add_patch(Rectangle((-P.BAY_L / 2, P.WL_BAY_BOTTOM), P.BAY_L, P.BAY_H,
                           fc=FILL_BAY, ec=INK, lw=LW_VISIBLE, hatch="///", zorder=5))

    pod = [(P.POD_NOSE_X, 330), (620, P.WL_FLOOR), (-460, P.WL_FLOOR),
           (P.POD_TAIL_X, 380), *POD_TOP_EDGE]
    ax.add_patch(Polygon(pod, closed=True, fc=FILL_STRUCT, ec=INK,
                         lw=LW_VISIBLE, zorder=4))
    ax.plot([-160, 240], [P.WL_SEAT, P.WL_SEAT], color=INK, lw=LW_THIN, zorder=6)
    _pilot_side(ax)

    # roll hoop lies in the YZ plane, so it projects to a straight line here
    ax.plot([HOOP_X, HOOP_X], [648, P.WL_HOOP_TOP], color=INK, lw=2.6, zorder=7)
    ax.plot([HOOP_X, HOOP_X], [P.WL_FLOOR, 648], color=HIDDEN, lw=1.1,
            ls=(0, (6, 3)), zorder=7)
    ax.plot([HOOP_X, P.POD_TAIL_X], [P.WL_HOOP_TOP - 110, 645],
            color=INK, lw=LW_THIN, zorder=6)

    # upper rail that carries the four boom roots, plus its posts and braces
    ax.plot([-P.BOOM_ROOT_X, P.BOOM_ROOT_X], [P.WL_BOOM_ROOT] * 2,
            color=INK, lw=2.0, zorder=6)
    for sx in (1, -1):
        ax.plot([sx * P.BOOM_ROOT_X] * 2,
                [P.WL_BOOM_ROOT, _pod_top_z(sx * P.BOOM_ROOT_X)],
                color=INK, lw=LW_VISIBLE, zorder=5)
        ax.plot([sx * P.BOOM_ROOT_X, sx * 120],
                [P.WL_BOOM_ROOT, _pod_top_z(sx * 120)],
                color=INK, lw=LW_THIN, zorder=5)

        root = (sx * P.BOOM_ROOT_X, P.WL_BOOM_ROOT)
        tip = (sx * P.ROTOR_X, P.WL_ROTOR_LOWER)
        ax.add_patch(Polygon(_boom_polygon(root, tip, P.ARM_BOOM_OD_MM * 0.85),
                             closed=True, fc=FILL_STRUCT, ec=INK,
                             lw=LW_VISIBLE, zorder=5))
        _rotor_disk_edge(ax, sx * P.ROTOR_X, P.WL_ROTOR_LOWER)

    # dihedral
    root = (P.BOOM_ROOT_X, P.WL_BOOM_ROOT)
    _centerline(ax, (root[0] - 60, P.WL_BOOM_ROOT), (root[0] + 640, P.WL_BOOM_ROOT))
    ax.add_patch(Arc(root, 1060, 1060, theta1=0, theta2=P.ARM_DIHEDRAL_DEG,
                     color=DIM, lw=LW_DIM, zorder=6))
    ax.text(root[0] + 250, P.WL_BOOM_ROOT - 150,
            f"{P.ARM_DIHEDRAL_DEG:.0f}\u00b0 DIHEDRAL", fontsize=8.0, color=DIM, zorder=7)

    # waterline ladder
    wl_x = -P.LENGTH / 2 - 300
    for wl, name in (
        (P.WL_GROUND, "WL 0   GROUND LINE"),
        (P.WL_BAY_BOTTOM, f"WL {P.WL_BAY_BOTTOM:.0f}   PACK FLOOR"),
        (P.WL_FLOOR, f"WL {P.WL_FLOOR:.0f}   CABIN FLOOR"),
        (P.WL_BOOM_ROOT, f"WL {P.WL_BOOM_ROOT:.0f}   BOOM ROOT"),
        (P.WL_ROTOR_LOWER, f"WL {P.WL_ROTOR_LOWER:.0f}   LWR ROTOR"),
        (P.WL_ROTOR_UPPER, f"WL {P.WL_ROTOR_UPPER:.0f}   UPR ROTOR"),
        (P.WL_HOOP_TOP, f"WL {P.WL_HOOP_TOP:.0f}   HOOP TOP"),
    ):
        ax.plot([wl_x, P.LENGTH / 2 + 60], [wl, wl], color=CENTER, lw=0.5,
                ls=(0, (2, 5)), zorder=2)
        ax.text(wl_x - 40, wl, name, ha="right", va="center", fontsize=7.0,
                color="#5b6470", zorder=7)

    _dim_v(ax, 0, P.WL_HOOP_TOP, P.LENGTH / 2 + 180, P.ROTOR_X + P.PROP_DISK_R,
           f"{P.HEIGHT:.0f}   OVERALL HEIGHT")
    _dim_v(ax, P.WL_ROTOR_LOWER, P.WL_ROTOR_UPPER, -P.ROTOR_X + 430,
           -P.ROTOR_X + P.PROP_DISK_R, f"{P.MOTOR_STACK:.0f}", fontsize=7.4)
    _dim_h(ax, -P.SKID_SPAN / 2, P.SKID_SPAN / 2, -170, 0,
           f"{P.SKID_SPAN:.0f} SKID", fontsize=7.4)

    ax.annotate("", xy=(P.LENGTH / 2 + 60, -265), xytext=(P.ROTOR_X - 120, -265),
                arrowprops=dict(arrowstyle="-|>,head_width=0.2,head_length=0.6",
                                lw=1.0, color=INK), zorder=7)
    ax.text(P.ROTOR_X - 160, -265, "NOSE", ha="right", va="center",
            fontsize=8.2, color=INK, zorder=7)

    _balloon(ax, 7, (HOOP_X, P.WL_HOOP_TOP - 40), (-1520, 1180))
    _balloon(ax, 8, (-120, P.WL_FLOOR + 60), (-1520, 440))


# ----------------------------------------------------------------------------
# FRONT ELEVATION
# ----------------------------------------------------------------------------
def draw_front(ax):
    _ground(ax, -P.WIDTH / 2 - 80, P.WIDTH / 2 + 80)
    hw = P.COCKPIT_W / 2.0

    for sy in (-1, 1):
        ax.plot([sy * P.SKID_TRACK / 2] * 2, [0, P.SKID_OD],
                color=INK, lw=4.0, solid_capstyle="round", zorder=6)
        ax.plot([sy * P.SKID_TRACK / 2, sy * hw * 0.75],
                [P.SKID_OD, P.WL_BAY_BOTTOM], color=INK, lw=LW_VISIBLE, zorder=6)

    ax.add_patch(Rectangle((-P.BAY_W / 2, P.WL_BAY_BOTTOM), P.BAY_W, P.BAY_H,
                           fc=FILL_BAY, ec=INK, lw=LW_VISIBLE, hatch="///", zorder=5))

    pod = [(-hw, P.WL_FLOOR), (hw, P.WL_FLOOR), (hw, 540), (hw * 0.70, 640),
           (-hw * 0.70, 640), (-hw, 540)]
    ax.add_patch(Polygon(pod, closed=True, fc=FILL_STRUCT, ec=INK,
                         lw=LW_VISIBLE, zorder=4))

    # roll hoop true-shape: vertical posts with a radiused crown at WL 1120
    crown_z = P.WL_HOOP_TOP - hw
    for sy in (-1, 1):
        ax.plot([sy * hw] * 2, [P.WL_FLOOR, crown_z], color=INK, lw=2.6, zorder=7)
    ax.add_patch(Arc((0, crown_z), P.COCKPIT_W, P.COCKPIT_W, theta1=0, theta2=180,
                     color=INK, lw=2.6, zorder=7))

    # pilot head + shoulders for scale
    ax.add_patch(Circle((0, 980), 105, fill=False, ec=HIDDEN, lw=1.0,
                        ls=(0, (7, 3)), zorder=7))
    ax.plot([-205, 205], [840, 840], color=HIDDEN, lw=1.0, ls=(0, (7, 3)), zorder=7)

    for sy in (-1, 1):
        root = (sy * P.BOOM_ROOT_Y, P.WL_BOOM_ROOT)
        tip = (sy * P.ROTOR_Y, P.WL_ROTOR_LOWER)
        ax.plot([sy * P.BOOM_ROOT_Y] * 2, [600, P.WL_BOOM_ROOT],
                color=INK, lw=2.0, zorder=6)
        ax.add_patch(Polygon(_boom_polygon(root, tip, P.ARM_BOOM_OD_MM * 0.85),
                             closed=True, fc=FILL_STRUCT, ec=INK,
                             lw=LW_VISIBLE, zorder=5))
        _rotor_disk_edge(ax, sy * P.ROTOR_Y, P.WL_ROTOR_LOWER)
        _axis_cross(ax, sy * P.ROTOR_Y, P.WL_ROTOR_LOWER, 150)

    _centerline(ax, (0, -100), (0, P.WL_HOOP_TOP + 190))

    _dim_h(ax, -P.WIDTH / 2, P.WIDTH / 2, -265, 0, f"{P.WIDTH:.0f}   OVERALL WIDTH")
    _dim_h(ax, -P.SKID_TRACK / 2, P.SKID_TRACK / 2, -130, 0,
           f"{P.SKID_TRACK:.0f} SKID TRACK", fontsize=7.4)
    _dim_h(ax, -P.ROTOR_Y, P.ROTOR_Y, P.WL_MAST_TOP + 200, P.WL_ROTOR_UPPER,
           f"{2 * P.ROTOR_Y:.0f}   ROTOR TRACK")
    _dim_v(ax, P.WL_FLOOR, P.WL_HOOP_TOP, -P.WIDTH / 2 - 60, -hw,
           f"{P.WL_HOOP_TOP - P.WL_FLOOR:.0f} CABIN", fontsize=7.4)


# ----------------------------------------------------------------------------
# panels
# ----------------------------------------------------------------------------
DATA_ROWS = (
    ("CONFIGURATION", f"{P.ARMS}-boom coaxial octorotor, 8 motors"),
    ("OVERALL L \u00d7 W \u00d7 H", f"{P.LENGTH:.0f} \u00d7 {P.WIDTH:.0f} \u00d7 {P.HEIGHT:.0f}"),
    ("ROTOR BASE \u00d7 TRACK", f"{2 * P.ROTOR_X:.0f} \u00d7 {2 * P.ROTOR_Y:.0f}"),
    ("ROTOR DISK", f"8 \u00d7 \u2300{P.PROP_DISK_D:.0f}, coaxial pairs"),
    ("DISK LOADING", f"{P.DISK_LOADING_KG_M2:.0f} kg/m\u00b2 at MTOW"),
    ("BOOM", f"\u2300{P.ARM_BOOM_OD_MM:.0f} \u00d7 {P.BOOM_LENGTH:.0f} lg, "
             f"{P.ARM_DIHEDRAL_DEG:.0f}\u00b0 dihedral"),
    ("TIP CLEARANCE", f"{P.PROP_GAP_LATERAL:.0f} lat / {P.PROP_GAP_LONGITUDINAL:.0f} long / "
                      f"{P.POD_TIP_CLEARANCE:.0f} pod"),
    ("EMPTY WEIGHT", f"{P.EMPTY_KG:.0f} kg (Part 103 limit {P.PART103_EMPTY_MAX_KG:.0f})"),
    ("MTOW", f"{P.MTOW_KG:.0f} kg (pilot \u2264 {P.PILOT_MAX_KG:.0f} kg)"),
    ("ENERGY", f"{P.BATTERY_KWH_NOMINAL:.1f} kWh nom / {P.BATTERY_KWH_USABLE:.1f} usable"),
    ("POWER", f"{P.AVG_POWER_KW:.0f} kW avg / {P.PEAK_POWER_KW:.0f} kW peak"),
    ("ENDURANCE", f"~{P.FLIGHT_TIME_MIN} min hover-dominated"),
    ("VNE (SOFTWARE)", f"{P.PART103_SPEED_MAX_KMH:.0f} km/h \u2014 55 kt"),
    ("PROPULSION", f"{P.PROPULSION_KIT} \u00d7 {P.PROPULSION_QTY}"),
    ("BATTERY", f"{P.BATTERY_VENDOR}, {P.BATTERY_VOLTAGE_S}S"),
    ("STRUCTURE", "6061-T6 aluminium, Aircraft Spruce"),
    ("BOOM AZIMUTH", f"{P.BOOM_AZIMUTH_DEG:.1f}\u00b0 off centreline"),
    ("ROTOR PLANES", f"WL {P.WL_ROTOR_LOWER:.0f} / WL {P.WL_ROTOR_UPPER:.0f}"),
    ("CABIN HEIGHT", f"{P.WL_HOOP_TOP - P.WL_FLOOR:.0f} floor to hoop crown"),
)

KEY_ROWS = (
    (1, "Coaxial rotor pair \u2014 T-MOTOR X-A12XL II-24S, props incl."),
    (2, f"Boom \u2014 \u2300{P.ARM_BOOM_OD_MM:.0f} tube, {P.BOOM_LENGTH:.0f} lg, bolted to truss corner"),
    (3, "Cockpit pod / keel truss \u2014 1 in sq 6061-T6 (03-38900)"),
    (4, f"Battery bay \u2014 {P.BAY_L:.0f} \u00d7 {P.BAY_W:.0f} \u00d7 {P.BAY_H:.0f}, "
        f"{P.BATTERY_KWH_NOMINAL:.1f} kWh, {P.BATTERY_MASS_KG:.0f} kg"),
    (5, "Roll hoop \u2014 1-1/8 in rd (03-00045) + 5-point harness"),
    (6, f"Skid rail \u2014 0.930 rd (03-34400), {P.SKID_SPAN:.0f} lg"),
    (7, "BRS ballistic parachute canister, above WL 1120"),
    (8, "Avionics bay \u2014 Cube Orange, ArduPilot coax-octo mix"),
)

NOTES = (
    "1.  DIMENSIONS IN MILLIMETRES.  THIRD-ANGLE PROJECTION.  DO NOT SCALE DRAWING.",
    "2.  DATUM:  X 0 AT POD FRAME STA 0;  Y 0 ON PLANE OF SYMMETRY;",
    "     Z 0 AT SKID GROUND LINE (WL 0).",
    "3.  OVERALL LENGTH AND WIDTH ARE TO ROTOR DISK TIPS, NOT TO STRUCTURE.",
    "4.  DIAGONALLY OPPOSITE ROTOR PAIRS COUNTER-ROTATE FOR YAW AUTHORITY.",
    "5.  PUBLISHED X-A12XL QUAD MTOW IS BELOW 210 kg.  THRUST-STAND EVERY",
    "     BOOM TO 52.5 kg MIN AND GET WRITTEN VENDOR SIGN-OFF BEFORE FLIGHT.",
    f"6.  DISK LOADING {P.DISK_LOADING_KG_M2:.0f} kg/m\u00b2 IS HIGH FOR A MANNED ROTORCRAFT;",
    "     THE ENDURANCE FIGURE IS HOVER-LIMITED.",
    "7.  PILOT SHOWN RECLINED TO CLEAR WL 1120.  VERIFY PER OCCUPANT.",
)


def _panel(ax, title=None):
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           fc=FILL_PANEL, ec=INK, lw=1.0, clip_on=False))
    if title:
        ax.text(0.5, 0.97, title, transform=ax.transAxes, ha="center", va="top",
                fontsize=10.5, fontweight="bold", color=INK)


def draw_data(ax):
    _panel(ax, "DESIGN DATA")
    top, bot = 0.905, 0.035
    step = (top - bot) / len(DATA_ROWS)
    for i, (k, v) in enumerate(DATA_ROWS):
        y = top - i * step
        ax.text(0.035, y, k, transform=ax.transAxes, fontsize=7.3,
                color="#5b6470", va="top")
        ax.text(0.40, y, v, transform=ax.transAxes, fontsize=7.6,
                color=INK, va="top")


def draw_key(ax):
    _panel(ax, "KEY")
    top, bot = 0.80, 0.06
    step = (top - bot) / len(KEY_ROWS)
    for i, (n, txt) in enumerate(KEY_ROWS):
        y = top - i * step
        ax.add_patch(Circle((0.042, y), 0.032, transform=ax.transAxes,
                            fc=PAPER, ec=INK, lw=0.8, clip_on=False))
        ax.text(0.042, y, str(n), transform=ax.transAxes, ha="center",
                va="center", fontsize=6.8, fontweight="bold", color=INK)
        ax.text(0.095, y, txt, transform=ax.transAxes, fontsize=7.2,
                color=INK, va="center")


def draw_notes(ax):
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           fc=PAPER, ec=INK, lw=1.0, clip_on=False))
    ax.text(0.018, 0.90, "NOTES", transform=ax.transAxes, fontsize=9.5,
            fontweight="bold", color=INK, va="top")
    top, bot = 0.70, 0.07
    step = (top - bot) / (len(NOTES) - 1)
    for i, n in enumerate(NOTES):
        ax.text(0.018, top - i * step, n, transform=ax.transAxes,
                fontsize=7.1, color=INK, va="center")


def draw_title_block(ax, scale_text):
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           fc=PAPER, ec=INK, lw=1.5, clip_on=False))
    ax.plot([0.50, 0.50], [0, 1], transform=ax.transAxes, color=INK, lw=1.0)
    for x in (0.66, 0.80):
        ax.plot([x, x], [0, 1], transform=ax.transAxes, color=INK, lw=0.8)
    ax.plot([0.50, 1.0], [0.5, 0.5], transform=ax.transAxes, color=INK, lw=0.8)

    ax.text(0.022, 0.86, "SOUTHEAST AERIAL SYSTEMS", transform=ax.transAxes,
            fontsize=7.6, color="#5b6470", va="center")
    ax.text(0.022, 0.60, "SEAS SOLO-1", transform=ax.transAxes, fontsize=16,
            fontweight="bold", color=INK, va="center")
    ax.text(0.022, 0.35, "GENERAL ARRANGEMENT", transform=ax.transAxes,
            fontsize=9.0, color=INK, va="center")

    # third-angle projection symbol
    cx, cy, rr = 0.075, 0.135, 0.036
    ax.add_patch(Circle((cx, cy), rr, transform=ax.transAxes, fill=False,
                        ec=INK, lw=0.9, clip_on=False))
    ax.add_patch(Circle((cx, cy), rr * 0.45, transform=ax.transAxes, fill=False,
                        ec=INK, lw=0.9, clip_on=False))
    ax.add_patch(Polygon([(cx + 0.055, cy + rr), (cx + 0.055, cy - rr),
                          (cx + 0.135, cy)], transform=ax.transAxes,
                         fill=False, ec=INK, lw=0.9, clip_on=False))
    ax.text(0.235, cy, "THIRD-ANGLE PROJECTION", transform=ax.transAxes,
            fontsize=6.6, color="#5b6470", va="center")

    def cell(x, y, label, value, *, size=10.5, weight="bold"):
        ax.text(x, y + 0.34, label, transform=ax.transAxes, fontsize=6.3,
                color="#5b6470", va="center")
        ax.text(x, y + 0.14, value, transform=ax.transAxes, fontsize=size,
                color=INK, va="center", fontweight=weight)

    cell(0.518, 0.5, "SCALE", scale_text)
    cell(0.518, 0.0, "UNITS", "mm", size=9.5, weight="normal")
    cell(0.675, 0.5, "SHEET", "1 OF 1", size=9.5, weight="normal")
    cell(0.675, 0.0, "REV", "C", size=9.5, weight="normal")
    cell(0.815, 0.5, "DRAWING NO.", "SEAS-S1-GA-001", size=9.0)
    cell(0.815, 0.0, "CATEGORY", "FAA PART 103", size=8.5, weight="normal")


# ----------------------------------------------------------------------------
# sheet assembly
# ----------------------------------------------------------------------------
PLAN_X = (-P.LENGTH / 2 - 900, P.LENGTH / 2 + 280)   # left band carries the WL ladder
PLAN_Y = (-P.WIDTH / 2 - 340, P.WIDTH / 2 + 120)
SIDE_Z = (-300.0, P.HEIGHT + 200)
FRONT_Y = (-P.WIDTH / 2 - 200, P.WIDTH / 2 + 200)


def export_sheet() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)

    plan_w_mm = PLAN_X[1] - PLAN_X[0]
    plan_h_mm = PLAN_Y[1] - PLAN_Y[0]
    side_h_mm = SIDE_Z[1] - SIDE_Z[0]
    front_w_mm = FRONT_Y[1] - FRONT_Y[0]

    block_w_mm = plan_w_mm + GAP_MM + front_w_mm
    block_h_mm = plan_h_mm + GAP_MM + side_h_mm

    fig = plt.figure(figsize=(SHEET_W, SHEET_H), facecolor=PAPER)
    border = fig.add_axes((0, 0, 1, 1))
    border.axis("off")
    mx, my = MARGIN / SHEET_W, MARGIN / SHEET_H
    border.add_patch(Rectangle((mx, my), 1 - 2 * mx, 1 - 2 * my, fill=False,
                               ec=INK, lw=1.8, transform=border.transAxes))

    banner_h, strip_h = 0.042, 0.148
    x0, x1 = mx + 0.014, 1 - mx - 0.014
    y_bot = my + 0.012 + strip_h + 0.018
    y_top = 1 - my - banner_h

    border.text((x0 + x1) / 2, 1 - my - 0.015,
                "SEAS SOLO-1   \u00b7   PART 103 COAXIAL OCTOROTOR   \u00b7   GENERAL ARRANGEMENT",
                ha="center", va="top", fontsize=15.5, fontweight="bold", color=INK)

    avail_w, avail_h = x1 - x0, y_top - y_bot - 0.024

    # snap to a preferred drawing scale that still fits the sheet
    s_fit = min(avail_w / block_w_mm * SHEET_W, avail_h / block_h_mm * SHEET_H)
    ratio = next((r for r in PREFERRED_SCALES if 1.0 / (25.4 * r) <= s_fit),
                 PREFERRED_SCALES[-1])
    s = 1.0 / (25.4 * ratio)

    fx, fy = s / SHEET_W, s / SHEET_H
    left_w, right_w = plan_w_mm * fx, front_w_mm * fx
    top_h, bot_h = plan_h_mm * fy, side_h_mm * fy
    gap_x, gap_y = GAP_MM * fx, GAP_MM * fy

    bx = x0
    by = y_bot + max(0.0, (avail_h - (top_h + gap_y + bot_h)) / 2.0)

    # the data panel absorbs any horizontal slack; the front view stays to scale
    col_x = bx + left_w + gap_x
    col_w = max(right_w, x1 - col_x)
    front_x = col_x + (col_w - right_w) / 2.0

    ax_plan = _view_axes(fig, (bx, by + bot_h + gap_y, left_w, top_h),
                         PLAN_X, PLAN_Y, "PLAN VIEW", "LOOKING DOWN")
    ax_side = _view_axes(fig, (bx, by, left_w, bot_h),
                         PLAN_X, SIDE_Z, "SIDE ELEVATION", "RIGHT SIDE")
    ax_front = _view_axes(fig, (front_x, by, right_w, bot_h),
                          FRONT_Y, SIDE_Z, "FRONT ELEVATION", "LOOKING AFT")
    ax_data = fig.add_axes((col_x, by + bot_h + gap_y, col_w, top_h))

    draw_plan(ax_plan)
    draw_side(ax_side)
    draw_front(ax_front)
    draw_data(ax_data)

    tb_w, key_w = 0.335, 0.255
    sy = my + 0.014
    ax_notes = fig.add_axes((x0, sy, (x1 - x0) - tb_w - key_w - 0.020, strip_h))
    ax_key = fig.add_axes((x1 - tb_w - key_w - 0.008, sy, key_w, strip_h))
    ax_tb = fig.add_axes((x1 - tb_w, sy, tb_w, strip_h))
    draw_notes(ax_notes)
    draw_key(ax_key)
    draw_title_block(ax_tb, f"1 : {ratio}")

    out = OUT / "solo1_general_arrangement.png"
    fig.savefig(out, dpi=150, facecolor=PAPER)
    plt.close(fig)
    print(f"wrote {out}  ({out.stat().st_size // 1024} KB)  scale 1:{ratio}")
    return out


if __name__ == "__main__":
    export_sheet()
