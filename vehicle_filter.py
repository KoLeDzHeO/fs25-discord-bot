import json

with open("fs25_vehicles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

vehicle_map = {entry["xml_key"]: entry for entry in data}

CATEGORY_ORDER = [
    "Трактор", "Комбайн", "Жатка", "Культиватор", "Сеялка", "Опрыскиватель",
    "Тюковый пресс", "Обмотчик тюков", "Погрузчик", "Прицеп",
    "Силосный погрузчик", "Грузовик", "Оборудование", "Неизвестная техника"
]

def get_info_by_key(xml_key):
    return vehicle_map.get(xml_key, {
        "icon": "🛠️",
        "name_ru": xml_key,
        "class": "Неизвестная техника",
        "fuel_capacity": None
    })

def get_icon_by_class(class_name):
    for v in vehicle_map.values():
        if v["class"] == class_name and v.get("icon"):
            return v["icon"]
    return "🛠️"

def format_status_line(xml_key, dirt, damage, fuel):
    info = get_info_by_key(xml_key)
    icon = info.get("icon", "🛠️")
    name = info.get("name_ru") or xml_key
    status = []

    if dirt > 0.05:
        status.append(f"грязь {int(dirt * 100)}%")
    if damage > 0.05:
        status.append(f"повреж. {int(damage * 100)}%")

    max_fuel = info.get("fuel_capacity") or 0
    if max_fuel and fuel < 0.8 * max_fuel:
        status.append(f"топл. {int(fuel)}L")

    stat_str = " | ".join(status)
    return f"  {icon} {name:<32} {stat_str}"
