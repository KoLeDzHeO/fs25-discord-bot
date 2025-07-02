import aiohttp
from typing import Optional
from config.config import config

# Загружает XML-файл с сервера Farming Simulator
async def fetch_xml(session: aiohttp.ClientSession, endpoint: str) -> Optional[str]:
    """Возвращает XML по указанному эндпойнту."""

    # Для stats.xml нужно заменить savegame.html на stats.xml
    if endpoint == "":
        url = (
            f"{config.api_base_url.replace('dedicated-server-savegame.html', 'dedicated-server-stats.xml')}"
            f"?code={config.api_secret_code}"
        )
    else:
        # Для остальных файлов используем параметр file
        url = f"{config.api_base_url}?file={endpoint}&code={config.api_secret_code}"

    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()
    except aiohttp.ClientError as e:
        # Сообщаем в консоль об ошибке загрузки
        print(f"❌ Ошибка загрузки файла '{endpoint}': {e}")
        return None


# Функция для получения данных careerSavegame (время, день, фермы, погода)
async def fetch_career_savegame(session: aiohttp.ClientSession) -> Optional[str]:
    return await fetch_xml(session, "careerSavegame")


# Функция для получения списка техники
async def fetch_vehicles(session: aiohttp.ClientSession) -> Optional[str]:
    return await fetch_xml(session, "vehicles")


# Функция для получения экономики (доходы, расходы)
async def fetch_economy(session: aiohttp.ClientSession) -> Optional[str]:
    return await fetch_xml(session, "economy")
