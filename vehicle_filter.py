import json

# Load vehicle information from the filtered list shipped with the bot
with open("filtered_vehicles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Map XML file key to the corresponding info dictionary
vehicle_map = {}
for entry in data:
    key = entry.get("nameXML") or entry.get("xml_key")
    if key:
        vehicle_map[key] = entry

# Build a mapping from class name to icon for quick lookup (may be empty)
class_icon_map = {
    entry["class"]: entry.get("icon") for entry in data if entry.get("class")
}

CATEGORY_ORDER = [
    "Трактор",
    "Комбайн",
    "Жатка",
    "Культиватор",
    "Сеялка",
    "Опрыскиватель",
    "Тюковый пресс",
    "Обмотчик тюков",
    "Погрузчик",
    "Прицеп",
    "Силосный погрузчик",
    "Грузовик",
    "Оборудование",
    "Неизвестная техника",
]


def get_info_by_key(xml_key):
    """Return info for the given XML key or sensible defaults."""
    return vehicle_map.get(
        xml_key,
        {
            "icon": "🛠️",
            "name": xml_key,
            "class": "Неизвестная техника",
            "fuel_capacity": None,
        },
    )


def get_icon_by_class(class_name):
    """Return icon for the given class name."""
    return class_icon_map.get(class_name, "🛠️")
