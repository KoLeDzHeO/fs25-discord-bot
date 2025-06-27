import xml.etree.ElementTree as ET
from typing import List
import json

# Загрузка JSON с каталогом культур
with open("data/crops_catalog.json", "r", encoding="utf-8") as f:
    crops_catalog = json.load(f)

def get_crop_name(code):
    for crop in crops_catalog:
        if crop["nameXML"] == code:
            return crop["name"]
    return "UNKNOWN"

def get_crop_emoji(code):
    for crop in crops_catalog:
        if crop["nameXML"] == code:
            return crop["emoji"]
    return "❓"

def get_crop_growth_max(code):
    for crop in crops_catalog:
        if crop["nameXML"] == code:
            return crop["growth_stages"]
    return 0

# Основной разбор статуса полей
def parse_field_statuses(xml_bytes: bytes) -> List[str]:
    tree = ET.fromstring(xml_bytes)
    fields = tree.findall(".//field")
    results = []

    for field in fields:
        №if field.get("farmId") != "1":
            continue

        field_id = field.get("id")
        fruit_type = field.get("fruitType", "UNKNOWN")
        growth = int(field.get("growthState", 0))
        weed = int(field.get("weed", 0))
        lime = int(field.get("lime", 0))
        spray = int(field.get("spray", 0))

        name = get_crop_name(fruit_type)
        emoji = get_crop_emoji(fruit_type)
        max_stage = get_crop_growth_max(fruit_type)

        if fruit_type == "UNKNOWN":
            status = f"{emoji} UNKNOWN | Пустое | можно сеять"
        elif growth >= max_stage:
            status = f"{emoji} {name} | Урожай готов"
        else:
            status = f"{emoji} {name} | Стадия {growth}/{max_stage}"

        if weed > 0:
            status += " | 🌱 Сорняки"
        if lime == 0:
            status += " | 🧂 Нет извести"
        if spray == 0:
            status += " | 💧 Нет удобрения"

        results.append(f"# {field_id} — {status}")

    return results
