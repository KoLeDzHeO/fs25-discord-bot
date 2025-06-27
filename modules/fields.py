from xml.etree import ElementTree as ET
from modules.crops import get_crop_name, get_crop_emoji, get_crop_growth_max
from config import config

def parse_field_statuses(xml_bytes: bytes) -> list[str]:
    """
    Разбирает fields.xml и возвращает список строк со статусами полей.
    Фильтрует по farmId, если атрибут присутствует.
    """
    tree = ET.fromstring(xml_bytes)
    fields = tree.findall(".//field")

    results: list[str] = []

    for field in fields:
        # Фильтрация по farmId (если атрибут есть и не совпадает с настройкой)
        farm_id = field.get("farmId")
        if farm_id is not None and farm_id != config.FARM_ID:
            continue

        field_id = field.get("id")
        fruit_type = field.get("fruitType", "UNKNOWN")
        growth = int(field.get("growthState", "0"))
        weed = int(field.get("weedState", "0"))
        lime = int(field.get("limeLevel", "0"))
        spray = int(field.get("sprayLevel", "0"))

        # Имя культуры и эмодзи
        name = get_crop_name(fruit_type)
        emoji = get_crop_emoji(fruit_type)
        max_stage = get_crop_growth_max(fruit_type)

        # Определяем статус по росту
        if fruit_type == "UNKNOWN":
            status = "🟫 Пустое | можно сеять"
        elif growth >= max_stage:
            status = f"{emoji} {name} | урожай готов 🧺"
        else:
            status = f"{emoji} {name} | стадия: {growth}/{max_stage}"

        # Добавляем дополнительные состояния
        if weed > 0:
            status += " | 🌱 сорняки"
        if lime == 0:
            status += " | 🧂 известь ❌"
        if spray == 0:
            status += " | 💧 удобрение ❌"

        results.append(f"# {field_id} {status}")

    return results
