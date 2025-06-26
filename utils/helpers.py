import json
import os
from typing import Iterable, List

from config import config


_vehicle_map: dict[str, dict] | None = None


def _load_vehicle_map() -> dict[str, dict]:
    global _vehicle_map
    if _vehicle_map is None:
        path = os.path.join(config.DATA_DIR, config.VEHICLES_FILE)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _vehicle_map = {}
        for entry in data:
            key = entry.get("nameXML") or entry.get("xml_key")
            if key:
                _vehicle_map[key] = entry
    return _vehicle_map


def get_info_by_key(xml_key: str) -> dict:
    mapping = _load_vehicle_map()
    return mapping.get(
        xml_key,
        {
            "icon": "🛠️",
            "name": xml_key,
            "class": "Неизвестная техника",
            "fuel_capacity": None,
        },
    )


def split_messages(sections: Iterable[str], max_length: int = 2000) -> List[str]:
    """Split long text into Discord-friendly message blocks."""
    blocks: List[str] = []
    current = ""
    for section in sections:
        for line in section.splitlines(keepends=True):
            if len(current) + len(line) > max_length:
                blocks.append(current.rstrip())
                current = ""
            current += line
        if len(current) > max_length:
            blocks.append(current.rstrip())
            current = ""
    if current.strip():
        blocks.append(current.rstrip())
    return blocks
