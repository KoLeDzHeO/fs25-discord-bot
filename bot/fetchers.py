import aiohttp
from typing import Optional

from config.config import config

async def fetch_xml(session: aiohttp.ClientSession, endpoint: str) -> Optional[str]:
    """Fetch XML data from the given endpoint."""
    url = f"{config.api_base_url}{endpoint}&code={config.api_secret_code}"
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()
    except aiohttp.ClientError as e:
        print(f"Failed to fetch {endpoint}: {e}")
        return None

async def fetch_career_savegame(session: aiohttp.ClientSession) -> Optional[str]:
    return await fetch_xml(session, "/file=careerSavegame")

async def fetch_vehicles(session: aiohttp.ClientSession) -> Optional[str]:
    return await fetch_xml(session, "/file=vehicles")

async def fetch_economy(session: aiohttp.ClientSession) -> Optional[str]:
    return await fetch_xml(session, "/file=economy")
