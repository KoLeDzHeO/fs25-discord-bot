import json

with open("fs25_vehicles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

vehicle_map = {entry["xml_key"]: entry for entry in data}
# Build a mapping from class name to icon for quick lookup
class_icon_map = {entry["class"]: entry.get("icon") for entry in data if entry.get("class")}

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
    """Return icon for the given class name."""
    return class_icon_map.get(class_name, "🛠️")

