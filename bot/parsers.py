import xml.etree.ElementTree as ET
from typing import Tuple, Optional


def parse_career_savegame(xml_text: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """Return map name, day number and time string."""
    root = ET.fromstring(xml_text)
    map_name = None
    day = None
    time = None

    # пробуем несколько вариантов для совместимости разных версий
    for tag in ("mapName", "mapTitle", "name"):
        elem = root.find(f".//{tag}")
        if elem is not None and elem.text:
            map_name = elem.text
            break

    for tag in ("day", "currentDay", "dayNumber"):
        elem = root.find(f".//{tag}")
        if elem is not None and elem.text:
            try:
                day = int(elem.text)
            except ValueError:
                pass
            break

    for tag in ("time", "currentTime", "dayTime"):
        elem = root.find(f".//{tag}")
        if elem is not None and elem.text:
            time = elem.text
            break

    return map_name, day, time


def parse_vehicles_count(xml_text: str) -> int:
    root = ET.fromstring(xml_text)
    return len(root.findall('.//vehicle'))


def parse_economy(xml_text: str) -> Tuple[Optional[int], Optional[int]]:
    """Return current balance and last day income (difference)."""
    root = ET.fromstring(xml_text)
    money_nodes = root.findall('.//money')
    if not money_nodes:
        return None, None

    try:
        current_balance = int(float(money_nodes[-1].text))
    except (ValueError, TypeError):
        current_balance = None

    money_change = None
    if len(money_nodes) >= 2:
        try:
            prev = int(float(money_nodes[-2].text))
            money_change = current_balance - prev if current_balance is not None else None
        except (ValueError, TypeError):
            pass
    return current_balance, money_change
