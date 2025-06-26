from typing import Iterable

from models import Vehicle


def classify_vehicles(vehicles: Iterable[Vehicle]) -> str:
    """Return formatted markdown describing vehicle statuses."""
    damaged: list[str] = []
    dirty: list[str] = []
    other: list[str] = []

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

    lines = []

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

