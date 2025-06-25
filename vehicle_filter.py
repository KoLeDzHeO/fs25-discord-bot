
import json

with open("fs25_vehicles.json", "r", encoding="utf-8") as f:
    vehicle_data = json.load(f)
    vehicle_map = {v["xml_key"].lower(): v for v in vehicle_data}

def get_vehicle_metadata(xml_key: str):
    return vehicle_map.get(xml_key.lower())

def needs_attention(xml_key: str, dirt: float, damage: float, fuel: float) -> bool:
    info = get_vehicle_metadata(xml_key)
    if not info:
        return True  # Показывать неизвестную технику

    if info.get("uses_fuel"):
        capacity = info.get("fuel_capacity", 0)
        return dirt > 0.05 or damage > 0.05 or fuel < 0.8 * capacity
    else:
        return dirt > 0.05 or damage > 0.05

def format_status(xml_key: str, dirt: float, damage: float, fuel: float) -> str:
    info = get_vehicle_metadata(xml_key)
    name = info.get("name_ru", xml_key)
    icon = info.get("icon", "")
    category = info.get("class", "Неизвестно")
    parts = []

    if dirt > 0.05:
        parts.append(f"Грязь: {int(dirt * 100)}%")
    if damage > 0.05:
        parts.append(f"Повреждение: {int(damage * 100)}%")
    if info.get("uses_fuel") and info.get("fuel_capacity"):
        if fuel < 0.8 * info["fuel_capacity"]:
            parts.append(f"Топливо: {int(fuel)}L")

    return f"{icon} {name} ({category}) | " + " | ".join(parts)
