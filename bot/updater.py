import aiohttp
import asyncio
from datetime import timedelta
import discord
from config.config import config
from ftp.fetcher import fetch_file
from .fetchers import fetch_stats_xml, fetch_api_file, fetch_dedicated_server_stats
from .parsers import parse_all, parse_players_online
from .discord_ui import build_embed
from utils.logger import log_debug
from utils.online_history import insert_online_players, make_online_graph
from utils.helpers import get_moscow_datetime

async def ftp_polling_task(bot: discord.Client, db_pool):
    log_debug("[TASK] Запущен ftp_polling_task")
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(config.channel_id)
    if channel is None:
        log_debug("❌ Канал не найден!")
        return

    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            log_debug("[FTP] Получаем dedicated-server-stats.xml")
            stats_xml = await fetch_stats_xml(session)
            log_debug("[API] Получаем vehicles")
            vehicles_xml = await fetch_api_file(session, "vehicles")
            log_debug("[FTP] Получаем careerSavegame.xml")
            career_ftp = await fetch_file("careerSavegame.xml")
            log_debug("[FTP] Получаем farmland.xml")
            farmland_ftp = await fetch_file("farmland.xml")
            log_debug("[FTP] Получаем farms.xml")
            farms_ftp = await fetch_file("farms.xml")
            log_debug("[FTP] Получаем dedicated-server-stats.xml (feed)")
            dedicated_server_stats_ftp = await fetch_dedicated_server_stats(session)

            log_debug(
                f"[DEBUG] Статусы: stats={bool(stats_xml)}, vehicles={bool(vehicles_xml)}, careerFTP={bool(career_ftp)}, farmlandFTP={bool(farmland_ftp)}, farms={bool(farms_ftp)}"
            )

            all_files_loaded = all([stats_xml, vehicles_xml, career_ftp, farmland_ftp, farms_ftp])
            if all_files_loaded:
                server_status = "🟢 Сервер работает"
                log_debug("[FTP] Все необходимые файлы загружены")
                data = parse_all(
                    server_stats=stats_xml,
                    vehicles_api=vehicles_xml,
                    career_savegame_ftp=career_ftp,
                    farmland_ftp=farmland_ftp,
                    farms_xml=farms_ftp,
                    dedicated_server_stats=dedicated_server_stats_ftp,
                )
                # данные успешно загружены
            else:
                server_status = "🔴 Сервер недоступен"
                data = {
                    "last_month_profit": None,
                    "server_name": None,
                    "map_name": None,
                    "slots_used": None,
                    "slots_max": None,
                    "farm_money": None,
                    "fields_owned": None,
                    "fields_total": None,
                    "vehicles_owned": None,
                    "players_online": [],
                }

            data["server_status"] = server_status
            embed = build_embed(data)

            graph_file = None
            if all_files_loaded:
                graph_file = await make_online_graph(db_pool)

            async for msg in channel.history(limit=None):
                try:
                    await msg.delete()
                except Exception as e:
                    log_debug(f"[Discord] Не удалось удалить сообщение: {e}")

            log_debug("[Discord] Отправляем сообщение")
            if graph_file:
                embed.set_image(url="attachment://online_graph.png")
                with open(graph_file, "rb") as f:
                    await channel.send(
                        embed=embed,
                        file=discord.File(f, filename="online_graph.png"),
                    )
            else:
                await channel.send(embed=embed)
            log_debug("[Discord] ✅ Embed успешно отправлен.")

            await asyncio.sleep(config.ftp_poll_interval)


async def api_polling_task(db_pool):
    """Периодически опрашивает API и сохраняет онлайн игроков."""
    async with aiohttp.ClientSession() as session:
        while True:
            stats_xml = await fetch_dedicated_server_stats(session)
            if stats_xml:
                players = parse_players_online(stats_xml)
                await insert_online_players(db_pool, players)
            await asyncio.sleep(config.api_poll_interval)


