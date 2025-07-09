import aiohttp
import asyncio
import discord
from datetime import datetime
from config.config import config
from ftp.fetcher import fetch_file
from .fetchers import fetch_stats_xml, fetch_api_file, fetch_dedicated_server_stats
from .parsers import parse_all, parse_players_online
from .discord_ui import build_embed
from utils.logger import log_debug

async def ftp_polling_task(bot: discord.Client):
    log_debug("[TASK] Запущен ftp_polling_task")
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(config.channel_id)
    if channel is None:
        log_debug("❌ Канал не найден!")
        return

    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            try:
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

                async for msg in channel.history(limit=None):
                    try:
                        await msg.delete()
                    except Exception as e:
                        log_debug(f"[Discord] Не удалось удалить сообщение: {e}")

                log_debug("[Discord] Отправляем сообщение")
                await channel.send(embed=embed)
                log_debug("[Discord] ✅ Embed успешно отправлен.")

                await asyncio.sleep(config.ftp_poll_interval)
            except Exception as e:
                log_debug(f"[TASK] ftp_polling_task error: {e}")
                await asyncio.sleep(5)


async def api_polling_task():
    """Периодически опрашивает API и сохраняет онлайн игроков."""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await fetch_dedicated_server_stats(session)
                await asyncio.sleep(config.api_poll_interval)
            except Exception as e:
                log_debug(f"[TASK] api_polling_task error: {e}")
                await asyncio.sleep(5)


async def save_online_history_task(bot: discord.Client):
    """Сохраняет список онлайн-игроков каждые 15 минут."""
    log_debug("[TASK] Запущен save_online_history_task")
    await bot.wait_until_ready()
    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            try:
                now = datetime.now()
                minute = now.minute

                now_utc = datetime.utcnow().replace(tzinfo=None)

                if minute % 15 == 0:
                    log_debug("[ONLINE] Время среза, получаем список игроков")
                    xml = await fetch_dedicated_server_stats(session)
                    players = parse_players_online(xml) if xml else []
                    log_debug(f"[ONLINE] Игроков онлайн: {len(players)}")
                    for name in players:
                        try:
                            await bot.db_pool.execute(
                                "INSERT INTO player_online_history (player_name, check_time, date, hour, dow)"
                                " VALUES ($1, $2, DATE($2), EXTRACT(HOUR FROM $2), EXTRACT(DOW FROM $2));",
                                name,
                                now,
                            )
                        except Exception as db_e:
                            log_debug(f"[DB] Ошибка записи игрока: {db_e}")

                    await asyncio.sleep(60)
                else:
                    wait_seconds = ((15 - (minute % 15)) * 60) - now.second
                    if wait_seconds <= 0:
                        wait_seconds = 1
                    log_debug(f"[ONLINE] Не время среза, ждём {wait_seconds} секунд")
                    await asyncio.sleep(wait_seconds)
            except Exception as e:
                log_debug(f"[TASK] save_online_history_task error: {e}")
                await asyncio.sleep(5)


