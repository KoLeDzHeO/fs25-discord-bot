import aiohttp

from config.config import config
from .logger import log_debug

async def fetch_stats_xml(session):
    url = f"{config.api_base_url.replace('dedicated-server-savegame.html', 'dedicated-server-stats.xml')}?code={config.api_secret_code}"
    log_debug(f"[API] Загружаем stats.xml по адресу: {url}")
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.text()
            log_debug("[API] stats.xml загружен успешно.")
            return data
    except Exception as e:
        log_debug(f"[API] ❌ Ошибка загрузки stats.xml: {e}")
        return None

async def fetch_api_file(session, filename):
    url = f"{config.api_base_url}?file={filename}&code={config.api_secret_code}"
    log_debug(f"[API] Загружаем файл {filename} по адресу: {url}")
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.text()
            log_debug(f"[API] {filename} загружен успешно.")
            return data
    except Exception as e:
        log_debug(f"[API] ❌ Ошибка загрузки {filename}: {e}")
        return None

async def fetch_dedicated_server_stats(session):
    """Загружает feed/dedicated-server-stats.xml"""
    url = f"{config.api_base_url.replace('dedicated-server-savegame.html', 'feed/dedicated-server-stats.xml')}?code={config.api_secret_code}"
    log_debug(f"[API] Загружаем dedicated-server-stats.xml по адресу: {url}")
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.text()
            log_debug("[API] dedicated-server-stats.xml загружен успешно.")
            return data
    except Exception as e:
        log_debug(f"[API] ❌ Ошибка загрузки dedicated-server-stats.xml: {e}")
        return None
