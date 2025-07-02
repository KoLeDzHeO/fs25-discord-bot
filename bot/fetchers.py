import aiohttp
from config.config import config

async def fetch_stats_xml(session):
    url = f"http://{config.api_base_url.replace('dedicated-server-savegame.html','dedicated-server-stats.xml')}?code={config.api_secret_code}"
    print(f"[API] Загружаем stats.xml по адресу: {url}")
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.text()
            print("[API] stats.xml загружен успешно.")
            return data
    except Exception as e:
        print(f"[API] ❌ Ошибка загрузки stats.xml: {e}")
        return None

async def fetch_api_file(session, filename):
    url = f"{config.api_base_url}?file={filename}&code={config.api_secret_code}"
    print(f"[API] Загружаем файл {filename} по адресу: {url}")
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.text()
            print(f"[API] {filename} загружен успешно.")
            return data
    except Exception as e:
        print(f"[API] ❌ Ошибка загрузки {filename}: {e}")
        return None
