from xml.etree import ElementTree as ET
from modules.crops import get_crop_name, get_crop_emoji, get_crop_growth_max

def parse_field_statuses(xml_bytes: bytes) -> list[str]:
    tree = ET.fromstring(xml_bytes)
    fields = tree.findall(".//field")

    results = []

    for field in fields:
        farm_id = field.get("farmId")
        if farm_id != "1":
            continue
        field_id = field.get("id")
        fruit_type = field.get("fruitType", "UNKNOWN")
        growth = int(field.get("growthState", 0))
        weed = int(field.get("weed", 0))
        lime = int(field.get("lime", 0))
        spray = int(field.get("spray", 0))

        # Имя и эмодзи
        name = get_crop_name(fruit_type)
        emoji = get_crop_emoji(fruit_type)
        max_stage = get_crop_growth_max(fruit_type)

        # Выводим стадию
        if fruit_type == "UNKNOWN":
            status = "🟫 Пустое | можно сеять"
        elif growth >= max_stage:
            status = f"{emoji} {name} | урожай готов 🧺"
        else:
            status = f"{emoji} {name} | стадия: {growth}/{max_stage}"

        # Добавим состояния
        if weed > 0:
            status += " | 🌱 сорняки"
        if lime == 0:
            status += " | 🧂 известь ❌"
        if spray == 0:
            status += " | 💧 удобрение ❌"

        results.append(f"# {field_id} {status}")

    return results
