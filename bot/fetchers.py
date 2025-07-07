import aiohttp

from config.config import config
from utils.logger import log_debug


async def _fetch(session: aiohttp.ClientSession, url: str, desc: str) -> str | None:
    """Загружает файл по указанному URL."""
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

async def fetch_stats_xml(session):
    url = (
        f"{config.api_base_url.replace('dedicated-server-savegame.html', 'dedicated-server-stats.xml')}?code={config.api_secret_code}"
    )
    return await _fetch(session, url, "stats.xml")

async def fetch_api_file(session, filename):
    url = f"{config.api_base_url}?file={filename}&code={config.api_secret_code}"
    return await _fetch(session, url, filename)

async def fetch_dedicated_server_stats(session):
    """Загружает feed/dedicated-server-stats.xml"""
    url = (
        f"{config.api_base_url.replace('dedicated-server-savegame.html', 'dedicated-server-stats.xml')}?code={config.api_secret_code}"
    )
    return await _fetch(session, url, "dedicated-server-stats.xml")

