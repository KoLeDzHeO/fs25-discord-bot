import sys
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

        if damage > 50 and fuel < 0.4 * capacity:
            damaged.append(f"• {name} — поврежд. {int(damage)}%, топливо: {int(fuel)}")
        elif dirt > 50:
            dirty.append(f"• {name} — грязь: {int(dirt)}%")
        elif damage > 5 or dirt > 5 or fuel < 0.8 * capacity:
            other.append(
                f"• {name} — грязь: {int(dirt)}%, поврежд.: {int(damage)}%, топливо: {int(fuel)}"
            )

    lines = ["📉 **Техника в критическом состоянии:**"]

    if damaged:
        lines.append("\n🛠️ **Повреждённая техника (низкое топливо + повреждение):**")
        lines.extend(damaged)

    if dirty:
        lines.append("\n💩 **Сильно загрязнённая техника:**")
        lines.extend(dirty)

    if other:
        lines.append("\n⚙️ **Остальная техника:**")
        lines.extend(other)

    return "\n".join(lines)


if __name__ == "__main__":
    example = [
        {"name": "Комбайн", "dirt": 60, "damage": 70, "fuel": 10, "fuel_capacity": 100},
        {"name": "Трактор", "dirt": 55, "damage": 10, "fuel": 80, "fuel_capacity": 120},
        {"name": "Прицеп", "dirt": 10, "damage": 0, "fuel": 0, "fuel_capacity": 0},
    ]
    markdown = classify_vehicles(example)
    print(markdown)

