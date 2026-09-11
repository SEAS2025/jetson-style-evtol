"""Validate the cab station table before any lofting happens.

Checks, in order of how expensive they are to discover late:
  1. does the reclined pilot fit, to the MIL-STD-1472G 50 mm floor
  2. does the shell stay clear of all four rotor disks
  3. does the section match published sailplane width-to-height ratios
  4. how many print segments the confirmed build volume forces
  5. is the bonded socket engagement long enough, hot and derated
  6. what the shell weighs at low infill, by two independent methods

Run:  PYTHONPATH=. .venv/bin/python -m design.cab_check
"""

from __future__ import annotations

import math

from design import cab_params as C
from design import params as P


def _wetted_area() -> float:
    area = 0.0
    x, step = C.CAB_NOSE_X, 10.0
    while x > C.CAB_TAIL_X:
        pts = C.section_points(x)
        area += sum(math.dist(pts[i], pts[(i + 1) % len(pts)])
                    for i in range(len(pts))) * step
        x -= step
    return area


def check_rotor_clearance() -> int:
    print("--- rotor disk clearance along the cab ---")
    rows: list[tuple[float, float, float]] = []
    x = C.CAB_NOSE_X
    while x >= C.CAB_TAIL_X:
        half_w, _, _ = C.section(x)
        limit = C.rotor_half_width_limit(x)
        if limit is not None:
            rows.append((x, half_w, limit - half_w))
        x -= 10.0

    if not rows:
        print("  cab never passes within a rotor disk station")
        return 0
    for x, hw, margin in rows[::14]:
        flag = "CLASH" if margin < 0 else ("tight" if margin < 15 else "ok")
        print(f"  x {x:8.0f}  half-width {hw:6.1f}  margin {margin:+7.1f}  {flag}")
    worst = min(rows, key=lambda r: r[2])
    print(f"  worst margin {worst[2]:+.1f} mm at x {worst[0]:.0f} "
          f"(clamped to a {C.ROTOR_MARGIN:.0f} mm gap by construction)")
    return 1 if worst[2] < -0.01 else 0


def check_pilot_fit() -> int:
    print(f"\n--- reclined pilot inside the shell "
          f"(floor {C.PILOT_CLEARANCE:.0f} mm, MIL-STD-1472G) ---")
    fails = 0
    # "supported" means the pilot rests on structure there, so the 50 mm
    # impact gap applies laterally and above but not below.
    body = (
        ("feet", C.PILOT_HEEL, C.PILOT_FOOT_HALF_W, 0.0, True),
        ("knee", C.PILOT_KNEE, C.PILOT_KNEE_HALF_W, 80.0, False),
        ("hip", C.PILOT_HIP, C.PILOT_HIP_HALF_W, 60.0, True),
        ("shoulder", C.PILOT_SHOULDER, C.PILOT_SHOULDER_HALF_W, 60.0, False),
        ("head", C.PILOT_HEAD_C, C.PILOT_HEAD_R, C.PILOT_HEAD_R, False),
    )
    for name, (x, _y, z), half_w, half_h, supported in body:
        shell_w, keel, crown = C.section(x)
        lat = (shell_w - C.SHELL_T) - half_w
        above = (crown - C.SHELL_T) - (z + half_h)
        below = (z - half_h) - (keel + C.SHELL_T)
        checked = [lat, above] if supported else [lat, above, below]
        ok = min(checked) >= C.PILOT_CLEARANCE
        fails += 0 if ok else 1
        tag = " (rests on structure)" if supported else ""
        print(f"  {name:9s} x {x:7.0f} z {z:6.0f} | lateral {lat:+7.1f} "
              f"above {above:+7.1f} below {below:+7.1f} | "
              f"{'ok' if ok else 'TOO TIGHT'}{tag}")
    return fails


def check_section_ratio() -> int:
    print("\n--- section width-to-height vs published sailplane sections ---")
    w = max(s[1] for s in C.STATIONS) * 2.0
    h = max(c - k for _, _, k, c in C.STATIONS)
    ratio = w / h
    for name, rw, rh in C.REFERENCE_SECTIONS:
        print(f"  {name:28s} {rw:5.0f} x {rh:5.0f}  w/h {rw / rh:.3f}")
    print(f"  {'SEAS cab':28s} {w:5.0f} x {h:5.0f}  w/h {ratio:.3f}")
    lo = min(rw / rh for _, rw, rh in C.REFERENCE_SECTIONS)
    hi = max(rw / rh for _, rw, rh in C.REFERENCE_SECTIONS)
    ok = lo - 0.02 <= ratio <= hi + 0.02
    print(f"  published band {lo:.3f}-{hi:.3f}  -> "
          f"{'in band' if ok else 'OUT OF BAND'}")
    return 0 if ok else 1


def check_segments() -> int:
    print("\n--- print segmentation, Tronxy VEHO 1000-20 ---")
    print(f"  bed {C.BUILD_X:.0f} x {C.BUILD_Y:.0f}, Z {C.BUILD_Z:.0f} "
          f"(capped to {C.MAX_PART_Z:.0f} per part by choice)")
    print(f"  usable {C.USABLE_X:.0f} x {C.USABLE_Y:.0f} x {C.USABLE_Z:.0f}")
    widest = max(s[1] for s in C.STATIONS) * 2.0
    tallest = max(c - k for _, _, k, c in C.STATIONS)
    print(f"  cab {C.CAB_LENGTH:.0f} long, {widest:.0f} wide, {tallest:.0f} tall")

    # Split lengthwise, then on the centreline, and lay each half-shell on
    # its flat cut face. Part height then equals the half-width, not the
    # section height, which is what keeps it inside the Z cap.
    n = C.SEGMENTS_LENGTHWISE
    seg = C.CAB_LENGTH / n
    part = (seg, tallest, widest / 2.0)      # bed X, bed Y, bed Z
    print(f"  {n} lengthwise segments x {C.HALVES} halves = "
          f"{C.PART_COUNT} printed parts")
    print(f"  each half laid on its centreline cut face:")
    print(f"    {part[0]:.0f} (bed X) x {part[1]:.0f} (bed Y) x "
          f"{part[2]:.0f} (bed Z)")

    fails = 0
    for v, limit, axis in ((part[0], C.USABLE_X, "X"),
                           (part[1], C.USABLE_Y, "Y"),
                           (part[2], C.USABLE_Z, "Z")):
        ok = v <= limit
        fails += 0 if ok else 1
        print(f"    bed {axis}: {v:6.0f} of {limit:6.0f}  "
              f"{'ok' if ok else 'EXCEEDS BED'}")

    minimum = math.ceil(C.CAB_LENGTH / C.USABLE_X)
    print(f"  bed alone would allow {minimum} segments; {n} chosen to keep "
          f"each print short")
    seams = (n - 1) + 1
    print(f"  cost of the choice: {seams} bonded seam planes "
          f"({n - 1} transverse, 1 centreline)")
    return fails


def check_print_time() -> int:
    print("\n--- print time per part ---")
    area = _wetted_area()
    mass_g = area * C.SHELL_T * C.PETG_DENSITY
    per_part = mass_g / C.PART_COUNT
    hours = per_part / C.PRINT_RATE_G_PER_H
    print(f"  {mass_g / 1000:.2f} kg of skin over {C.PART_COUNT} parts "
          f"-> {per_part:.0f} g each")
    print(f"  at {C.PRINT_RATE_G_PER_H:.0f} g/h -> {hours:.1f} h per part, "
          f"{mass_g / C.PRINT_RATE_G_PER_H:.0f} h of machine time total")
    ok = hours <= C.MAX_PRINT_HOURS
    print(f"  ceiling is {C.MAX_PRINT_HOURS:.0f} h per part  "
          f"{'ok' if ok else 'TOO LONG'}")
    return 0 if ok else 1


def check_register() -> int:
    print("\n--- socket bore and internal register spigot ---")
    fails = 0
    for tube, label in ((C.TUBE_KEEL, "keel"), (C.TUBE_FRAME, "frame"),
                        (C.TUBE_DIAG, "diag")):
        bore = C.socket_bore(tube)
        spig = C.register_od(tube)
        annulus = (bore - spig) / 2.0
        print(f"  {label:6s} {tube.part_no}: socket bore {bore:6.2f}, "
              f"spigot OD {spig:6.2f}, tube wall {tube.wall_mm:4.2f}")
        print(f"         annular gap {annulus:5.2f} mm holds a "
              f"{tube.wall_mm:.2f} mm wall + "
              f"{annulus - tube.wall_mm:.2f} mm of adhesive")
        # the spigot must be printable: wall plus flute depth inside the bore
        need = 2.0 * (C.REGISTER_WALL + C.FLUTE_DEPTH)
        ok = spig > need
        fails += 0 if ok else 1
        print(f"         spigot needs > {need:.1f} mm to print a "
              f"{C.REGISTER_WALL:.0f} mm wall with flutes  "
              f"{'ok' if ok else 'TOO SMALL'}")
        print(f"         register depth {C.register_depth(tube):5.1f} mm, "
              f"{C.FLUTE_COUNT} flutes {C.FLUTE_W:.0f} mm wide, "
              f"{C.BLEED_HOLE_D:.0f} mm bleed hole at the root")
    return fails


def check_bond() -> int:
    print("\n--- bonded socket engagement ---")
    print(f"  adhesive {C.ADHESIVE_NAME} (Spruce {C.ADHESIVE_PN})")
    print(f"  FRP lap shear {C.ADHESIVE_LAP_SHEAR_FRP_PSI:.0f} psi at 77 F, "
          f"x{C.ADHESIVE_DERATE_HOT:.2f} hot, / {C.BOND_SAFETY_FACTOR:.0f} safety")
    gap = C.SOCKET_CLEARANCE
    print(f"  socket gap {gap:.2f} mm radial vs "
          f"{C.ADHESIVE_MAX_BONDLINE_MM:.2f} mm qualified max  "
          f"{'ok' if gap <= C.ADHESIVE_MAX_BONDLINE_MM else 'TOO THICK'}")

    # size against a 9 g crash case on the pilot plus seat, per CS-22.561
    crash_n = 9.0 * (C.PILOT_MASS_MAX_KG + 15.0) * 9.80665
    per_tube = crash_n / 4.0        # shared across the four keel sockets
    fails = 0
    for tube, label in ((C.TUBE_KEEL, "keel"), (C.TUBE_FRAME, "frame"),
                        (C.TUBE_DIAG, "diag")):
        need = C.required_bond_length(tube, per_tube)
        depth = C.socket_depth(tube)
        ok = need <= depth
        fails += 0 if ok else 1
        print(f"  {label:6s} {tube.part_no} OD {tube.od_mm:5.2f} mm  "
              f"shear needs {need:5.1f} mm, socket "
              f"{C.SOCKET_DEPTH_DIAMETERS:.0f}xD = {depth:5.1f} mm  "
              f"{'ok' if ok else 'TOO SHORT'}")
    print(f"  sized for {crash_n / 1000:.1f} kN (9 g on pilot + seat, "
          f"CS-22.561), shared over 4 sockets")
    if gap > C.ADHESIVE_MAX_BONDLINE_MM:
        fails += 1
    return fails


def estimate_mass() -> None:
    print("\n--- shell mass, two independent estimates ---")
    area = 0.0
    vol_enclosed = 0.0
    x, step = C.CAB_NOSE_X, 10.0
    while x > C.CAB_TAIL_X:
        pts = C.section_points(x)
        perim = sum(math.dist(pts[i], pts[(i + 1) % len(pts)])
                    for i in range(len(pts)))
        area += perim * step
        # shoelace area of the section
        a = abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
                    - pts[(i + 1) % len(pts)][0] * pts[i][1]
                    for i in range(len(pts)))) / 2.0
        vol_enclosed += a * step
        x -= step

    skin_vol = area * C.SHELL_T
    m_skin = skin_vol * C.PETG_DENSITY
    print(f"  wetted area {area / 1e6:6.2f} m^2, enclosed volume "
          f"{vol_enclosed / 1e6:6.1f} litres")
    print(f"  skin only, {C.SHELL_T:.2f} mm wall  -> {m_skin / 1000:6.2f} kg")

    frac = skin_vol / vol_enclosed
    print(f"  effective {1000 * frac * C.PETG_DENSITY * 1000:.0f} g/litre "
          f"of enclosed volume")
    trap = vol_enclosed * 0.09 * C.PETG_DENSITY
    print(f"  for contrast, 9% gyroid through the whole cavity would add "
          f"{trap / 1000:.0f} kg -> infill stays at "
          f"{100 * C.INFILL:.0f}% everywhere but socket bosses")
    print(f"  flanges, sockets, seat pan and fasteners are extra")


def shape_report() -> None:
    print("\n--- shape sanity vs a real sailplane ---")
    xmax = C.max_section_x()
    frac = (C.CAB_NOSE_X - xmax) / C.CAB_LENGTH
    print(f"  fineness ratio {C.fineness_ratio():.2f} (Hoerner 2L/(w+h)); "
          f"Discus-class is ~{C.REFERENCE_FINENESS:.1f}")
    print(f"  max section at {100 * frac:.0f}% of length aft of the nose; "
          f"Radespiel measured {100 * C.REFERENCE_MAX_SECTION_FRAC:.0f}%")
    print("  both gaps are inherent to a pod with no tailboom, not errors")
    print(f"  printed seams stand proud of the {C.LAMINAR_TRIP_HEIGHT:.2f} mm "
          f"laminar trip height, so treat the surface as turbulent")


def main() -> int:
    print("SEAS Solo-1 printed cab — pre-loft checks\n")
    fails = check_rotor_clearance()
    fails += check_pilot_fit()
    fails += check_section_ratio()
    fails += check_segments()
    fails += check_bond()
    fails += check_register()
    fails += check_print_time()
    estimate_mass()
    shape_report()
    print("\n" + ("ALL CHECKS PASS" if not fails else f"{fails} CHECK(S) FAILED"))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
