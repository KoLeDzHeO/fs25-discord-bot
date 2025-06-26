import asyncio
import discord

from config import config
from ftp import client as ftp_client
from modules.vehicles import parse_vehicles, classify_vehicles
from utils.helpers import split_messages
from .discord_ui import create_report_embed

intents = discord.Intents.default()
client = discord.Client(intents=intents)

_last_messages: list[discord.Message] = []


@client.event
async def on_ready():
    print(f"Бот запущен как {client.user}")
    await start_reporting()


async def start_reporting() -> None:
    channel = client.get_channel(config.DISCORD_CHANNEL_ID)
    if not channel:
        print(f"❌ Канал с ID {config.DISCORD_CHANNEL_ID} не найден!")
        return

    async for msg in channel.history(limit=None):
        if msg.author == client.user:
            try:
                await msg.delete()
            except Exception as exc:
                print(f"⚠️ Не удалось удалить сообщение: {exc}")

    while True:
        for msg in _last_messages:
            try:
                await msg.delete()
            except Exception:
                pass
        _last_messages.clear()

        xml_data = await ftp_client.fetch_file(config.FTP_PATH)
        if not xml_data:
            msg = await channel.send("❌ Не удалось подключиться к FTP")
            _last_messages.append(msg)
            await asyncio.sleep(30)
            continue

        vehicles = parse_vehicles(xml_data)
        if not vehicles:
            msg = await channel.send("ℹ️ Нет техники для обслуживания")
            _last_messages.append(msg)
            await asyncio.sleep(30)
            continue

        markdown = classify_vehicles(vehicles)
        for block in split_messages([markdown]):
            embed = create_report_embed(block)
            sent = await channel.send(embed=embed)
            _last_messages.append(sent)

        await asyncio.sleep(config.CHECK_INTERVAL)


if __name__ == "__main__":
    client.run(config.DISCORD_TOKEN)
