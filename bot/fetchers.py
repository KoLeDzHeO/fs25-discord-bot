import aiohttp
from typing import Optional
from config.config import config

# Загружает XML-файл с сервера Farming Simulator по имени файла (например, "vehicles")
async def fetch_xml(session: aiohttp.ClientSession, file: str) -> Optional[str]:
    """
    Загружает XML по ссылке: BASE_URL?code=...&file=...
    """
    url = f"{config.api_base_url}?code={config.api_secret_code}&file={file}"

    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()
    except aiohttp.ClientError as e:
        print(f"❌ Ошибка загрузки файла '{file}': {e}")
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
