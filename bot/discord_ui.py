from datetime import datetime
from typing import Any, Dict

import discord


def build_embed(data: Dict[str, Any]) -> discord.Embed:
    """Формирует embed по данным, полученным из ``parse_all``."""

    # Извлекаем данные из словаря или ставим прочерк, если их нет
    server_name = data.get("server_name") or "—"
    map_name = data.get("map_name") or "—"
    print(f"[DEBUG PARSE_ALL] Сервер: {server_name}, Карта: {map_name}")
    slots_used = data.get("slots_used")
    slots_max = data.get("slots_max")
    farm_money = data.get("farm_money")
    def format_money(amount):
        try:
            amount = int(amount)
        except Exception:
            return str(amount)
        return f"{amount:,} $".replace(",", " ")
    profit = data.get("profit")
    profit_positive = data.get("profit_positive")
    fields_owned = data.get("fields_owned")
    fields_total = data.get("fields_total")
    vehicles_owned = data.get("vehicles_owned")
    last_updated = data.get("last_updated") or "—"

    slots_str = f"{slots_used if slots_used is not None else '—'} / {slots_max if slots_max is not None else '—'}"

    # Форматируем прибыль с учётом знака и emoji
    if profit is None:
        profit_str = "—"
    else:
        emoji = "🟢" if profit_positive is True else "🔴" if profit_positive is False else "—"
        profit_str = f"{profit:+} {emoji}"

    money_str = f"{format_money(farm_money)} / {format_money(month_profit)} ({month_period})"
    fields_str = f"{fields_owned if fields_owned is not None else '—'} / {fields_total if fields_total is not None else '—'}"
    vehicles_str = f"{vehicles_owned if vehicles_owned is not None else '—'}"

    # Текст embed'a формируем единой строкой
    description = "\n".join(
        [
            f"🧷 **Сервер:** {server_name} | {map_name}",
            f"👥 **Слоты:** {slots_str}",
            f"💰 **Деньги фермы:** {money_str}",
            f"🌾 **Поля во владении:** {fields_str}",
            f"🚜 **Техника:** {vehicles_str} единиц",
            f"📅 **Обновлено:** {last_updated}",
        ]
    )

    embed = discord.Embed(
        title="Состояние сервера Farming Simulator",
        description=description,
        color=0x00AAFF,
    )

    # Добавляем информацию о времени обновления бота
    embed.set_footer(text=f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return embed
