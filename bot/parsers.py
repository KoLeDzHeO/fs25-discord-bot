import xml.etree.ElementTree as ET
from typing import Tuple, Optional, Dict


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


def parse_server_stats(xml_text: str) -> Tuple[Optional[str], Optional[str], Optional[int], Optional[int], Optional[str]]:
    """Извлекает общую информацию о сервере."""
    root = ET.fromstring(xml_text)
    server_elem = root  # <Server> — корень

    server_name = server_elem.get('name')
    map_name = server_elem.get('mapName')

    slots_elem = server_elem.find('.//Slots')
    slots_max = None
    slots_used = None
    if slots_elem is not None:
        cap = slots_elem.get('capacity')
        used = slots_elem.get('numUsed')
        if cap is not None:
            try:
                slots_max = int(cap)
            except ValueError:
                pass
        if used is not None:
            try:
                slots_used = int(used)
            except ValueError:
                pass

    stats_elem = root.find('.//Stats')
    last_updated = stats_elem.get('saveDateFormatted') if stats_elem is not None else None

    return server_name, map_name, slots_used, slots_max, last_updated


def parse_farm_money(xml_text: str) -> Optional[int]:
    """Получает баланс фермы из careerSavegame.xml на FTP."""
    root = ET.fromstring(xml_text)
    elem = root.find('.//statistics/money')
    if elem is not None and elem.text:
        try:
            return int(float(elem.text))
        except (ValueError, TypeError):
            return None
    return None


def parse_daily_profit(xml_text: str) -> Tuple[Optional[int], Optional[bool]]:
    """Возвращает прибыль последнего дня и флаг её знака."""
    root = ET.fromstring(xml_text)
    stats = root.findall('.//dailyStat')
    if not stats:
        return None, None

    last = stats[-1]
    income = last.get('income') or last.get('earnings')
    expenses = last.get('expenses') or last.get('costs')

    try:
        inc = int(float(income)) if income is not None else 0
    except (ValueError, TypeError):
        inc = 0
    try:
        exp = int(float(expenses)) if expenses is not None else 0
    except (ValueError, TypeError):
        exp = 0

    profit = inc - exp
    return profit, profit >= 0


def _count_vehicles(xml_text: str, farm_id: str) -> Optional[int]:
    """Подсчёт техники в файле vehicles."""
    root = ET.fromstring(xml_text)
    vehicles = root.findall('.//vehicle')
    if not vehicles:
        return 0

    keywords = ['pallet', 'tree', 'wood', 'object', 'trailerWood', 'camera']

    has_farmid = any(v.get('farmId') is not None for v in vehicles)
    if not has_farmid:
        return None

    count = 0
    for v in vehicles:
        if v.get('farmId') == farm_id:
            filename = v.get('filename', '')
            if not any(k in filename for k in keywords):
                count += 1
    return count


def parse_farmland(xml_text: str, farm_id: str) -> Tuple[int, int]:
    """Подсчитывает количество полей у фермы."""
    root = ET.fromstring(xml_text)
    farmlands = root.findall('.//Farmland') or root.findall('.//farmland')
    total = len(farmlands)
    owned = len([f for f in farmlands if f.get('owner') == farm_id])
    return owned, total

def parse_month_profit(farms_xml: str, farm_id: str = '1', days_per_month: int = 30) -> Tuple[int, str]:
    """
    Считает суммарную прибыль/убыток за игровой месяц по farms.xml.
    Возвращает (прибыль, диапазон дней или название месяца).
    """
    root = ET.fromstring(farms_xml)
    farm_elem = None
    for farm in root.findall('.//farm'):
        if farm.get('farmId') == farm_id:
            farm_elem = farm
            break
    if farm_elem is None:
        return 0, "?"

    finances = farm_elem.find('finances')
    if finances is None:
        return 0, "?"

    stats_elems = finances.findall('stats')
    if not stats_elems:
        return 0, "?"

    # определяем последний игровой день
    last_day = int(stats_elems[-1].attrib["day"])
    # начало месяца (каждые 30 дней)
    month_start = ((last_day - 1) // days_per_month) * days_per_month + 1
    month_end = month_start + days_per_month - 1

    profit = 0.0
    for stats in stats_elems:
        day = int(stats.attrib["day"])
        if month_start <= day <= month_end:
            for child in stats:
                try:
                    profit += float(child.text)
                except (TypeError, ValueError):
                    continue
    month_name = f"дни {month_start}-{min(month_end, last_day)}"
    return int(profit), month_name

def parse_last_month_profit(xml_text: str) -> Optional[int]:
    """Возвращает округлённую прибыль за последний месяц (day=0) из farms.xml"""
    root = ET.fromstring(xml_text)
    stats = root.find(".//farm[@farmId='1']/finances/stats[@day='0']")
    if stats is None:
        return None

    profit = 0.0
    for elem in stats:
        try:
            profit += float(elem.text)
        except (ValueError, TypeError):
            pass

    return round(profit)



def parse_all(
    server_stats: str,
    career_savegame_api: str,
    vehicles_api: str,
    economy_api: str,
    career_savegame_ftp: str,
    farmland_ftp: str,
    vehicles_ftp: Optional[str] = None,
    farms_xml: Optional[str] = None,
    farm_id: str = '1'
) -> Dict[str, Optional[int]]:
    """Собирает все данные из разных источников и возвращает единую структуру."""

    server_name, map_name, slots_used, slots_max, last_updated = parse_server_stats(server_stats)

    farm_money = parse_farm_money(career_savegame_ftp)

    profit, positive = parse_daily_profit(economy_api)

    fields_owned, fields_total = parse_farmland(farmland_ftp, farm_id)

    vehicles_owned = _count_vehicles(vehicles_api, farm_id)
    if vehicles_owned is None and vehicles_ftp is not None:
        vehicles_owned = _count_vehicles(vehicles_ftp, farm_id)
    if vehicles_owned is None:
        vehicles_owned = 0

    print(f"[DEBUG PARSE_ALL] Сервер: {server_name}, Карта: {map_name}")

        # Расчёт месячной прибыли
    month_profit, month_period = 0, "-"
    if farms_xml is not None:
        month_profit, month_period = parse_month_profit(farms_xml, farm_id)

    result = {
        'month_profit': month_profit,
        'month_period': month_period,
        'server_name': server_name,
        'map_name': map_name,
        'slots_used': slots_used,
        'slots_max': slots_max,
        'farm_money': farm_money,
        'profit': profit,
        'profit_positive': positive,
        'fields_owned': fields_owned,
        'fields_total': fields_total,
        'vehicles_owned': vehicles_owned,
        'last_updated': last_updated,
    }

    return result
