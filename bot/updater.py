import json
import aiohttp
import asyncio
import discord
from typing import Optional
from pathlib import Path

from config.config import config
from .fetchers import fetch_career_savegame, fetch_vehicles, fetch_economy
from .parsers import parse_career_savegame, parse_vehicles_count, parse_economy
from .discord_ui import build_embed


async def load_message_id() -> Optional[int]:
    path = Path(config.message_id_file)
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return int(data.get("message_id"))
        except (ValueError, json.JSONDecodeError):
            return None
    return None


def save_message_id(message_id: int) -> None:
    Path(config.message_id_file).write_text(json.dumps({"message_id": message_id}))


async def update_message(bot: discord.Client):
    await bot.wait_until_ready()
    channel = bot.get_channel(config.channel_id)
    if channel is None:
        print("Channel not found")
        return

    message_id = await load_message_id()
    message = None
    if message_id:
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            message = None

    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            career_xml = await fetch_career_savegame(session)
            vehicles_xml = await fetch_vehicles(session)
            economy_xml = await fetch_economy(session)

            if career_xml and vehicles_xml and economy_xml:
                map_name, day, time_str = parse_career_savegame(career_xml)
                vehicle_count = parse_vehicles_count(vehicles_xml)
                balance, diff = parse_economy(economy_xml)

                embed = build_embed(map_name or "?", day or 0, time_str or "?", vehicle_count, balance or 0, diff or 0)

                # Если есть предыдущее сообщение, пытаемся удалить его
                if message is not None:
                    try:
                        await message.delete()
                    except discord.NotFound:
                        # Сообщение уже удалено или не существует
                        pass
                    except Exception as e:
                        # Логируем ошибку, но продолжаем работу цикла
                        print(f"⚠ Не удалось удалить сообщение: {e}")

                # Отправляем новый embed и сохраняем его ID
                message = await channel.send(embed=embed)
                save_message_id(message.id)

            await asyncio.sleep(config.ftp_poll_interval)
