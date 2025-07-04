import aiohttp
import asyncio
import discord         # <--- ВОТ ЭТА СТРОКА!
from config.config import config
from ftp.fetcher import fetch_file
from .fetchers import fetch_stats_xml, fetch_api_file
from .parsers import parse_all
from .discord_ui import build_embed
from .logger import log_debug

async def update_message(bot: discord.Client):
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(config.channel_id)
    if channel is None:
        log_debug("❌ Канал не найден!")
        return

    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            stats_xml = await fetch_stats_xml(session)
            vehicles_xml = await fetch_api_file(session, "vehicles")
            career_ftp = await fetch_file("careerSavegame.xml")
            farmland_ftp = await fetch_file("farmland.xml")
            farms_ftp = await fetch_file("farms.xml")
            dedicated_server_stats_ftp = await fetch_file("dedicated-server-stats.xml")

            log_debug(
                f"[DEBUG] Статусы: stats={bool(stats_xml)}, vehicles={bool(vehicles_xml)}, careerFTP={bool(career_ftp)}, farmlandFTP={bool(farmland_ftp)}, farms={bool(farms_ftp)}"
            )

            if all([stats_xml, vehicles_xml, career_ftp, farmland_ftp, farms_ftp]):
                data = parse_all(
                    server_stats=stats_xml,
                    vehicles_api=vehicles_xml,
                    career_savegame_ftp=career_ftp,
                    farmland_ftp=farmland_ftp,
                    farms_xml=farms_ftp,
                    dedicated_server_stats=dedicated_server_stats_ftp,
                )
                embed = build_embed(data)

                async for msg in channel.history(limit=None):
                    try:
                        await msg.delete()
                    except Exception as e:
                        log_debug(f"[Discord] Не удалось удалить сообщение: {e}")

                await channel.send(embed=embed)
                log_debug("[Discord] ✅ Embed успешно отправлен.")
            else:
                log_debug("[DEBUG] Не все данные загружены, пропускаем обновление.")

            await asyncio.sleep(config.ftp_poll_interval)
