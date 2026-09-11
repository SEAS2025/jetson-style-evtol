"""Aircraft Spruce & Specialty parts used in SEAS Solo-1 frame (dimensions in mm)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SprucePart:
    part_no: str
    description: str
    url: str
    unit: str
    notes: str = ""


INCH = 25.4

# --- Primary airframe tubing (6061-T6) ---
TUBE_1SQ = {
    "part_no": "03-38900",
    "od_mm": 1.0 * INCH,
    "wall_mm": 0.065 * INCH,
    "desc": "6061-T6 square tube 1 x 1 x 0.065",
    "url": "https://www.aircraftspruce.com/catalog/pnpages/03-38900.php",
}

TUBE_34SQ = {
    "part_no": "03-00009",
    "od_mm": 0.75 * INCH,
    "wall_mm": 0.049 * INCH,
    "desc": "6061-T6 square tube 3/4 x 3/4 x 0.049",
    "url": "https://www.aircraftspruce.com/catalog/pnpages/03-00009.php",
}

TUBE_1RD = {
    "part_no": "03-00045",
    "od_mm": 1.120 * INCH,
    "wall_mm": 0.065 * INCH,
    "desc": "6061-T6 round tube 1-1/8 OD x 0.065 wall",
    "url": "https://www.aircraftspruce.com/catalog/mepages/alumtubing-rd.php",
}

TUBE_34RD = {
    "part_no": "03-34400",
    "od_mm": 0.930 * INCH,
    "wall_mm": 0.065 * INCH,
    "desc": "6061-T6 round tube 0.930 OD x 0.065 wall (skid rail)",
    "url": "https://www.aircraftspruce.com/catalog/mepages/alumtubing-rd.php",
}

# --- Hardware ---
PARTS: dict[str, SprucePart] = {
    "rod_end_motor": SprucePart(
        "05-17037",
        "McFarlane rod end MCS1105-3 (3/16 bore, 10-32 ext)",
        "https://www.aircraftspruce.com/catalog/pnpages/05-17037.php",
        "ea",
        "Motor mount articulation / fold hinge",
    ),
    "rod_end_frame": SprucePart(
        "04-03454",
        "Heim HF-3M rod end (3/16 bore, 10-32)",
        "https://www.aircraftspruce.com/catalog/appages/heimHFseries.php",
        "ea",
        "Arm fold lock / jury fitting",
    ),
    "bolt_an3": SprucePart(
        "AN3-6A",
        "AN3 bolt 10-32 undrilled (example grip)",
        "https://www.aircraftspruce.com/catalog/stpages/anbolts.php",
        "ea",
        "Gusset and bracket joints — pick length per joint",
    ),
    "nut_ms21042": SprucePart(
        "MS21042-3",
        "MS21042-3 all-metal stop nut 10-32",
        "https://www.aircraftspruce.com/catalog/pnpages/MS21042-3.php",
        "ea",
    ),
    "washer_an960": SprucePart(
        "AN960-10",
        "AN960-10 flat washer for AN3",
        "https://www.aircraftspruce.com/catalog/pnpages/AN960-3.php",
        "ea",
    ),
    "rivet_an470": SprucePart(
        "AN470AD4",
        "AN470 universal-head solid rivet 1/8 dia (example)",
        "https://www.aircraftspruce.com/catalog/mepages/solidrivets.php",
        "ea",
        "Gusset-to-tube where bolted joints are impractical",
    ),
    "harness": SprucePart(
        "13-01300",
        "Style No. 5 seat belt / harness set (homebuilt)",
        "https://www.aircraftspruce.com/catalog/appages/seatbelt5.php",
        "set",
        "Open cockpit — mount to roll hoop with 1/4 in AN bolt",
    ),
    "parachute": SprucePart(
        "13-20942",
        "BRS Top VLS Genesis ultralight parachute system",
        "https://www.aircraftspruce.com/catalog/pnpages/13-20942.php",
        "kit",
        "Top mount — verify MTOW with BRS for ~210 kg config",
    ),
    "wire_m22759": SprucePart(
        "11-XXXXX",
        "MIL-W-22759/32 wire (select gauge per load)",
        "https://www.aircraftspruce.com/catalog/mepages/wire.php",
        "ft",
        "Power bus — order by AWG from Spruce wire section",
    ),
}
