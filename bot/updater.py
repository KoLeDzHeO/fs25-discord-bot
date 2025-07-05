import aiohttp
import asyncio
from pathlib import Path
import discord         # <--- ВОТ ЭТА СТРОКА!
from config.config import config
from ftp.fetcher import fetch_file
from .fetchers import fetch_stats_xml, fetch_api_file
from .parsers import parse_all
from .discord_ui import build_embed
from .logger import log_debug
from .online_history import (
    update_online_history,
    make_online_graph,
)

async def fetch_dedicated_server_stats(session):
    url = "http://195.179.229.189:8120/feed/dedicated-server-stats.xml?code=DsPF35gzLKvJNG8k"
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.text()
        return None

async def update_message(bot: discord.Client):
    print("=== [LOG] Фоновый таск update_message стартовал ===")
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(config.channel_id)
    if channel is None:
        log_debug("❌ Канал не найден!")
        return

    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            print("=== [LOG] Пробуем скачать файл: dedicated-server-stats.xml ===")
            stats_xml = await fetch_stats_xml(session)
            print("=== [LOG] Пробуем скачать файл: vehicles ===")
            vehicles_xml = await fetch_api_file(session, "vehicles")
            print("=== [LOG] Пробуем скачать файл: careerSavegame.xml ===")
            career_ftp = await fetch_file("careerSavegame.xml")
            print("=== [LOG] Пробуем скачать файл: farmland.xml ===")
            farmland_ftp = await fetch_file("farmland.xml")
            print("=== [LOG] Пробуем скачать файл: farms.xml ===")
            farms_ftp = await fetch_file("farms.xml")
            print("=== [LOG] Пробуем скачать файл: dedicated-server-stats.xml (ftp) ===")
            dedicated_server_stats_ftp = await fetch_dedicated_server_stats(session)

            log_debug(
                f"[DEBUG] Статусы: stats={bool(stats_xml)}, vehicles={bool(vehicles_xml)}, careerFTP={bool(career_ftp)}, farmlandFTP={bool(farmland_ftp)}, farms={bool(farms_ftp)}"
            )

            all_files_loaded = all([stats_xml, vehicles_xml, career_ftp, farmland_ftp, farms_ftp])
            if all_files_loaded:
                server_status = "🟢 Сервер работает"
                print("=== [LOG] Все необходимые файлы успешно загружены ===")
                data = parse_all(
                    server_stats=stats_xml,
                    vehicles_api=vehicles_xml,
                    career_savegame_ftp=career_ftp,
                    farmland_ftp=farmland_ftp,
                    farms_xml=farms_ftp,
                    dedicated_server_stats=dedicated_server_stats_ftp,
                )
                # Фиксируем онлайн каждого часа
                history_updated = await update_online_history(
                    data.get("players_online", [])
                )
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
                history_updated = False

            data["server_status"] = server_status
            embed = build_embed(data)

            graph_file = None
            if all_files_loaded:
                if history_updated or not Path("online_graph.png").exists():
                    graph_file = await make_online_graph()
                else:
                    graph_file = "online_graph.png"

            async for msg in channel.history(limit=None):
                try:
                    await msg.delete()
                except Exception as e:
                    log_debug(f"[Discord] Не удалось удалить сообщение: {e}")

            print("=== [LOG] Публикуем embed в Discord-канале ===")
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
