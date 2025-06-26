from typing import List, Dict


def classify_vehicles(vehicles: List[Dict]) -> str:
    """Return formatted markdown with vehicle statuses."""
    damaged = []
    dirty = []
    other = []

    for v in vehicles:
        name = v.get("name", "?")
        dirt = float(v.get("dirt", 0))
        damage = float(v.get("damage", 0))
        fuel = float(v.get("fuel", 0))
        capacity = float(v.get("fuel_capacity", 0)) or 1
        uses_fuel = v.get("uses_fuel", capacity > 0)

        is_damaged = damage > 50 or (uses_fuel and fuel < 0.4 * capacity)
        is_dirty = dirt > 50
        is_other = damage > 5 or dirt > 5

        if is_damaged:
            msg_parts = [f"поврежд. {int(damage)}%"]
            if uses_fuel:
                msg_parts.append(f"топливо: {int(fuel)}")
            msg = f"• {name} — " + ", ".join(msg_parts)
            damaged.append(msg)
        elif is_dirty:
            msg_parts = [f"грязь: {int(dirt)}%"]
            if damage >= 5:
                msg_parts.append(f"поврежд.: {int(damage)}%")
            if uses_fuel and fuel < 0.8 * capacity:
                msg_parts.append(f"топливо: {int(fuel)}")
            msg = f"• {name} — " + ", ".join(msg_parts)
            dirty.append(msg)
        elif is_other:
            msg_parts = []
            if dirt > 5:
                msg_parts.append(f"грязь: {int(dirt)}%")
            if damage > 5:
                msg_parts.append(f"поврежд.: {int(damage)}%")
            if uses_fuel and fuel < 0.8 * capacity:
                msg_parts.append(f"топливо: {int(fuel)}")
            msg = f"• {name} — " + ", ".join(msg_parts)
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


if __name__ == "__main__":
    example = [
        {
            "name": "Техника 1",
            "dirt": 60,
            "damage": 70,
            "fuel": 10,
            "fuel_capacity": 100,
        },
        {
            "name": "Техника 2",
            "dirt": 55,
            "damage": 10,
            "fuel": 80,
            "fuel_capacity": 120,
        },
        {"name": "Техника 3", "dirt": 10, "damage": 0, "fuel": 0, "fuel_capacity": 0},
    ]
    markdown = classify_vehicles(example)
    print(markdown)
