
import json

# Загрузка информации о технике из JSON
with open("fs25_vehicles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Преобразуем список в словарь по xml_key
vehicle_map = {entry["xml_key"]: entry for entry in data}

def get_info_by_key(xml_key):
    return vehicle_map.get(xml_key, {
        "icon": "🛠️",
        "name_ru": xml_key,
        "class": "Неизвестная техника"
    })

def format_status(xml_key, dirt, damage, fuel):
    info = get_info_by_key(xml_key)
    icon = info.get("icon", "🛠️")
    name_ru = info.get("name_ru") or xml_key
    category = info.get("class") or "Неизвестная техника"

    # Название техники
    line = f"{icon} {name_ru} — {category}"

    # Параметры состояния
    stats = []
    if dirt > 0:
        stats.append(f"Грязь: {int(dirt * 100)}%")
    if damage > 0:
        stats.append(f"Повреждение: {int(damage * 100)}%")
    if fuel > 0:
        stats.append(f"Топливо: {int(fuel)} L")

    if stats:
        line += "\n  ├ " + "  ".join(stats)

    return line
