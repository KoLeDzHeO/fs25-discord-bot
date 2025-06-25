import json

with open("fs25_vehicles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

vehicle_map = {entry["xml_key"]: entry for entry in data}

CATEGORY_ORDER = [
    "Грузовик", "Трактор", "Комбайн", "Жатка", "Разбрасыватель навоза",
    "Культиватор", "Сеялка", "Сеялка прямого высева", "Сеялка‑высевашка",
    "Опрыскиватель", "Прицеп", "Погрузчик", "Обмотчик тюков",
    "Тюковый пресс", "Квадратный тюковый пресс", "Круглый тюковый пресс",
    "Силосный погрузчик", "Оборудование", "Неизвестная техника"
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
