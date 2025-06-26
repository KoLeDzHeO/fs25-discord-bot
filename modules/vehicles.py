from dataclasses import dataclass
import xml.etree.ElementTree as ET
from typing import Iterable, List

from config import config
from utils.helpers import get_info_by_key


@dataclass
class Vehicle:
    name: str
    dirt: float
    damage: float
    fuel: float
    fuel_capacity: float
    uses_fuel: bool


SKIP_OBJECTS = {
    "eggBoxPallet",
    "cementBagsPallet",
    "bigBag_seeds",
    "bigBagHelm_fertilizer",
    "bigBag_fertilizer",
    "goatMilkCanPallet",
    "roofPlatesPallet",
    "cementBricksPallet",
    "cementBoxPallet",
}


def _extract_vehicle_levels(vehicle: ET.Element) -> tuple[float, float, float]:
    """Return dirt, damage and fuel levels for a vehicle element."""
    dirt = damage = fuel = 0.0
    dirt_elem = vehicle.find(".//washable/dirtNode")
    if dirt_elem is not None:
        dirt = float(dirt_elem.attrib.get("amount", 0))
    damage_elem = vehicle.find("wearable")
    if damage_elem is not None:
        damage = float(damage_elem.attrib.get("damage", 0))
    for unit in vehicle.findall(".//fillUnit/unit"):
        if unit.attrib.get("fillType", "").lower() == "diesel":
            fuel = float(unit.attrib.get("fillLevel", 0))
            break
    return dirt, damage, fuel


def parse_vehicles(xml_data: bytes) -> List[Vehicle]:
    """Parse vehicle information from XML data."""
    result: List[Vehicle] = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != config.FARM_ID:
                continue
            filename_raw = vehicle.get("filename")
            if not filename_raw:
                continue
            filename = filename_raw.split("/")[-1].replace(".xml", "")
            if filename in SKIP_OBJECTS:
                continue

            dirt, damage, fuel = _extract_vehicle_levels(vehicle)
            info = get_info_by_key(filename)
            max_fuel = info.get("fuel_capacity") or 0
            uses_fuel = info.get("uses_fuel", bool(max_fuel))

            if (
                damage <= 0.05
                and dirt <= 0.05
                and (not max_fuel or fuel >= 0.8 * max_fuel)
            ):
                continue

            result.append(
                Vehicle(
                    name=info.get("name") or filename,
                    dirt=dirt * 100,
                    damage=damage * 100,
                    fuel=fuel,
                    fuel_capacity=max_fuel,
                    uses_fuel=uses_fuel,
                )
            )
    except Exception as exc:
        print(f"XML parse error: {exc}")
    return result


def classify_vehicles(vehicles: Iterable[Vehicle]) -> str:
    """Return formatted markdown describing vehicle statuses."""
    damaged: List[str] = []
    dirty: List[str] = []
    other: List[str] = []

    names = [v.name for v in vehicles]
    max_name_len = max((len(n) for n in names), default=0)
    indent = "    "

    for v in vehicles:
        name = v.name
        dirt = float(v.dirt)
        damage = float(v.damage)
        fuel = float(v.fuel)
        capacity = float(v.fuel_capacity) or 1
        uses_fuel = v.uses_fuel

        is_damaged = damage > 50 or (uses_fuel and fuel < 0.4 * capacity)
        is_dirty = dirt > 50
        is_other = damage > 5 or dirt > 5

        formatted_name = f"{name:<{max_name_len}}"

        if is_damaged:
            msg_parts = [f"поврежд. {int(damage)}%"]
            if uses_fuel:
                msg_parts.append(f"топливо: {int(fuel)}")
            msg = f"{indent}• {formatted_name} — " + ", ".join(msg_parts)
            damaged.append(msg)
        elif is_dirty:
            msg_parts = [f"грязь: {int(dirt)}%"]
            if damage >= 5:
                msg_parts.append(f"поврежд.: {int(damage)}%")
            if uses_fuel and fuel < 0.8 * capacity:
                msg_parts.append(f"топливо: {int(fuel)}")
            msg = f"{indent}• {formatted_name} — " + ", ".join(msg_parts)
            dirty.append(msg)
        elif is_other:
            msg_parts = []
            if dirt > 5:
                msg_parts.append(f"грязь: {int(dirt)}%")
            if damage > 5:
                msg_parts.append(f"поврежд.: {int(damage)}%")
            if uses_fuel and fuel < 0.8 * capacity:
                msg_parts.append(f"топливо: {int(fuel)}")
            msg = f"{indent}• {formatted_name} — " + ", ".join(msg_parts)
            other.append(msg)

    lines: List[str] = []

    if damaged:
        prefix = "" if not lines else "\n"
        lines.append(
            f"{prefix}🛠️ **Повреждённая техника (низкое топливо + повреждение):**"
        )
        lines.extend(damaged)

    if dirty:
        prefix = "" if not lines else "\n"
        lines.append(f"{prefix}💩 **Сильно загрязнённая техника:**")
        lines.extend(dirty)

    if other:
        prefix = "" if not lines else "\n"
        lines.append(f"{prefix}⚙️ **Остальная техника:**")
        lines.extend(other)

    return "\n".join(lines)
