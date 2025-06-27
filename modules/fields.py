from xml.etree import ElementTree as ET
from modules.crops import get_crop_name, get_crop_emoji, get_crop_growth_max
from config import config

def parse_field_statuses(xml_bytes: bytes) -> list[str]:
    """
    Возвращает список строк: "#ID Emoji Название: текущая/макс [| флаги]".
    """
    root = ET.fromstring(xml_bytes)
    fields = root.findall(".//field")
    results: list[str] = []

    for field in fields:
        # фильтрация по farmId
        farm_id = field.get("farmId")
        if farm_id is not None and farm_id != config.FARM_ID:
            continue

        fid = field.get("id")
        ftype = field.get("fruitType", "UNKNOWN").upper()
        growth = int(field.get("growthState", "0"))

        # получаем данные из crops
        name = get_crop_name(ftype)
        emoji = get_crop_emoji(ftype)
        max_stage = get_crop_growth_max(ftype)

        # формируем базовую часть
        # если нет культуры
        if name == "Неизвестно":
            base = f"{emoji} Пустое: 0/{max_stage}"
        else:
            base = f"{emoji} {name}: {growth}/{max_stage}"

        # собираем флаги
        flags = []
        if int(field.get("weedState", "0")) > 0:
            flags.append("🌱")
        if int(field.get("limeLevel", "0")) == 0:
            flags.append("🧂")
        if int(field.get("sprayLevel", "0")) == 0:
            flags.append("💧")

        # итоговая строка
        line = f"#{fid} {base}"
        if flags:
            line += " | " + " ".join(flags)

        results.append(line)

    return results
