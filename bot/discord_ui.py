from datetime import datetime
import discord


def build_embed(map_name: str, day: int, time_str: str, vehicles: int, balance: int, diff: int) -> discord.Embed:
    """Генерирует embed-сообщение с игровой информацией."""
    embed = discord.Embed(title="Состояние сервера Farming Simulator", color=0x00AAFF)
    embed.add_field(name="🏷 Сервер", value=map_name or "?", inline=False)
    embed.add_field(name="📅 Игровое время", value=f"День {day}, {time_str}", inline=False)
    embed.add_field(name="🚜 Техники на сервере", value=str(vehicles), inline=False)
    if balance is not None and diff is not None:
        sign = "🟢" if diff >= 0 else "🔴"
        diff_str = f"{sign} {diff:+}" if diff != 0 else f"{diff:+}"
        embed.add_field(name="💰 Баланс фермы", value=f"{balance} / {diff_str}", inline=False)
    elif balance is not None:
        embed.add_field(name="💰 Баланс фермы", value=str(balance), inline=False)
    else:
        embed.add_field(name="💰 Баланс фермы", value="?", inline=False)
    embed.set_footer(text=f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return embed
