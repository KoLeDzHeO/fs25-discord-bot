"""Placeholder for field analysis logic."""

import xml.etree.ElementTree as ET


def parse_field_statuses(xml_bytes: bytes) -> list[str]:
    """Parse fields.xml and return formatted status lines."""
    result: list[str] = []
    try:
        root = ET.fromstring(xml_bytes)
        for elem in root.findall(".//field"):
            num = elem.get("number") or elem.get("id") or "?"
            fruit = (elem.get("fruitType") or "").upper()
            growth = int(elem.get("growthState", "0"))
            weeds = int(elem.get("weedState", "0"))
            lime = float(elem.get("limeLevel", "0"))
            plow = float(elem.get("plowLevel", "0"))
            spray = float(elem.get("sprayLevel", "0"))

            if not fruit or fruit == "NONE":
                result.append(f"#{num} 🟫 Пустое | можно сеять")
                continue

            parts = [f"#{num} 🌾 {fruit}"]
            if growth >= 7:
                parts.append("🧺 Урожай готов")
            else:
                parts.append(f"стадия: {growth}/7")

            parts.append(f"💧 удобрение: {int(spray * 100)}%")
            parts.append(f"🌱 сорняки: {'✅' if weeds else '❌'}")
            parts.append(f"🧂 известь: {'✅' if lime else '❌'}")
            parts.append(f"🔨 вспашка: {'✅' if plow else '❌'}")

            result.append(" | ".join(parts))
    except Exception as exc:
        print(f"XML parse error: {exc}")
    return result


def analyze_fields(data: bytes) -> str:
    return "Анализ полей пока не реализован"
