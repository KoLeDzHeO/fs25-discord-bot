"""Helpers for fetching files from the API."""

from typing import Optional, Tuple

import aiohttp

from config.config import config
from utils.logger import log_debug
from ftp.fetcher import fetch_file


async def _fetch(session: aiohttp.ClientSession, url: str, desc: str) -> Optional[str]:
    """Fetch a file from the given ``url`` using the provided session."""
    log_debug(f"[API] Загружаем {desc} по адресу: {url}")
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.text()
            log_debug(f"[API] {desc} загружен успешно.")
            return data
    except Exception as e:
        log_debug(f"[API] ❌ Ошибка загрузки {desc}: {e}")
        return None


async def fetch_api_file(session: aiohttp.ClientSession, filename: str) -> Optional[str]:
    """Download a file from the API by name."""
    url = f"{config.api_base_url}?file={filename}&code={config.api_secret_code}"
    return await _fetch(session, url, filename)


async def fetch_dedicated_server_stats(session: aiohttp.ClientSession) -> Optional[str]:
    """Download ``dedicated-server-stats.xml`` from the API feed."""
    url = (
        f"{config.api_base_url.replace('dedicated-server-savegame.html', 'dedicated-server-stats.xml')}?code={config.api_secret_code}"
    )
    return await _fetch(session, url, "dedicated-server-stats.xml")


async def fetch_required_files(bot) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Fetch all files required for building server stats."""
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        log_debug("[FTP] Получаем dedicated-server-stats.xml")
        stats_xml = await fetch_dedicated_server_stats(session)
        log_debug("[API] Получаем vehicles")
        vehicles_xml = await fetch_api_file(session, "vehicles")

    log_debug("[FTP] Получаем careerSavegame.xml")
    career_ftp = await fetch_file("careerSavegame.xml")
    log_debug("[FTP] Получаем farmland.xml")
    farmland_ftp = await fetch_file("farmland.xml")
    log_debug("[FTP] Получаем farms.xml")
    farms_ftp = await fetch_file("farms.xml")

    return stats_xml, vehicles_xml, career_ftp, farmland_ftp, farms_ftp
