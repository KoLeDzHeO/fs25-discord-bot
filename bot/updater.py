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
                map_name, day, time_str = parse_career_savegame(career_xml)
                vehicle_count = parse_vehicles_count(vehicles_xml)
                balance, diff = parse_economy(economy_xml)

                embed = build_embed(
                    map_name or "?",
                    day or 0,
                    time_str or "?",
                    vehicle_count,
                    balance or 0,
                    diff or 0,
                )

                # Удаляем все предыдущие сообщения в канале
                async for msg in channel.history(limit=None):
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Не удалось удалить сообщение: {e}")

                # Отправляем новый embed
                await channel.send(embed=embed)

            await asyncio.sleep(config.ftp_poll_interval)
