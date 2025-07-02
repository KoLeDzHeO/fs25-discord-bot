import aiohttp
import asyncio
import discord

from config.config import config
from .fetchers import fetch_career_savegame, fetch_vehicles, fetch_economy, fetch_xml
from ftp.fetcher import fetch_file
from .parsers import parse_all
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
            # Загружаем XML-файлы с API
            stats_xml = await fetch_xml(session, "serverStats")
            career_xml = await fetch_career_savegame(session)
            vehicles_xml = await fetch_vehicles(session)
            economy_xml = await fetch_economy(session)

            # Загружаем файлы с FTP
            career_ftp = await fetch_file("careerSavegame.xml")
            farmland_ftp = await fetch_file("farmland.xml")

            # Если все необходимые данные получены, разбираем их одной функцией
            if (
                stats_xml
                and career_xml
                and vehicles_xml
                and economy_xml
                and career_ftp
                and farmland_ftp
            ):
                data = parse_all(
                    server_stats=stats_xml,
                    career_savegame_api=career_xml,
                    vehicles_api=vehicles_xml,
                    economy_api=economy_xml,
                    career_savegame_ftp=career_ftp,
                    farmland_ftp=farmland_ftp,
                )

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
