import aiohttp
import asyncio
import discord

from config.config import config
from .fetchers import fetch_career_savegame, fetch_vehicles, fetch_economy
from .parsers import parse_career_savegame, parse_vehicles_count, parse_economy
from .discord_ui import build_embed


async def update_message(bot: discord.Client):
    """Периодически обновляет сообщение в канале."""
    await bot.wait_until_ready()
    # Получаем объект канала через fetch_channel
    channel = await bot.fetch_channel(config.channel_id)
    if channel is None:
        print("Channel not found")
        return

    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            career_xml = await fetch_career_savegame(session)
            vehicles_xml = await fetch_vehicles(session)
            economy_xml = await fetch_economy(session)

            if career_xml and vehicles_xml and economy_xml:
                # Получаем название карты, остальные параметры нам не нужны
                map_name, _, _ = parse_career_savegame(career_xml)
                vehicle_count = parse_vehicles_count(vehicles_xml)
                balance, diff = parse_economy(economy_xml)

                # Формируем структуру данных для embed
                data = {
                    "server_name": None,
                    "map_name": map_name,
                    "slots_used": None,
                    "slots_max": None,
                    "farm_money": balance,
                    "profit": diff,
                    "profit_positive": diff >= 0 if diff is not None else None,
                    "fields_owned": None,
                    "fields_total": None,
                    "vehicles_owned": vehicle_count,
                    "last_updated": None,
                }

                embed = build_embed(data)

                # Удаляем все предыдущие сообщения в канале
                async for msg in channel.history(limit=None):
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Не удалось удалить сообщение: {e}")

                # Отправляем новый embed
                await channel.send(embed=embed)

            await asyncio.sleep(config.ftp_poll_interval)
