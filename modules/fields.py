from xml.etree import ElementTree as ET
from modules.crops import get_crop_name, get_crop_emoji, get_crop_growth_max
from config import config

def parse_field_statuses(xml_bytes: bytes) -> list[str]:
    """
    Разбирает fields.xml и возвращает список строк со статусами полей
    с понятными русскими названиями и эмодзи из modules/crops.py.
    """
    tree = ET.fromstring(xml_bytes)
    fields = tree.findall(".//field")

    results: list[str] = []
    for field in fields:
        # Фильтрация по farmId (если задан и не совпадает)  
        farm_id = field.get("farmId")
        if farm_id is not None and farm_id != config.FARM_ID:
            continue

        # Основные параметры поля
        field_id = field.get("id")
        fruit_type = field.get("fruitType", "UNKNOWN").upper()
        growth = int(field.get("growthState", "0"))
        weed = int(field.get("weedState", "0"))
        lime = int(field.get("limeLevel", "0"))
        spray = int(field.get("sprayLevel", "0"))

        # Получаем русское название и эмодзи
        name = get_crop_name(fruit_type)
        emoji = get_crop_emoji(fruit_type)
        max_stage = get_crop_growth_max(fruit_type)

        # Формируем статус роста
        if fruit_type == "UNKNOWN" or name == "Неизвестно":
            growth_status = "Пустое | можно сеять"
        elif growth >= max_stage:
            growth_status = f"{emoji} {name} | Урожай готов"
        else:
            growth_status = f"{emoji} {name} | Стадия {growth}/{max_stage}"

        # Состояние поля
        flags: list[str] = []
        if weed > 0:
            flags.append("🌱 Сорняки")
        if lime == 0:
            flags.append("🧂 Нет извести")
        if spray == 0:
            flags.append("💧 Нет удобрения")

        # Объединяем в одну строку
        status_parts = [growth_status]
        if flags:
            status_parts.append(" | ".join(flags))
        status_line = f"# {field_id} — " + " | ".join(status_parts)
        results.append(status_line)

    return results
