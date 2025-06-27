import asyncio
import discord

from config import config
from ftp import client as ftp_client
from modules.vehicles import parse_vehicles, classify_vehicles
from modules.fields import parse_field_statuses
from utils.helpers import split_messages
from .discord_ui import create_report_embed

intents = discord.Intents.default()
client = discord.Bot(intents=intents)

_last_messages: list[discord.Message] = []


@client.slash_command(name="поля", description="Показать статус всех полей")
async def show_fields(ctx: discord.ApplicationContext):
    await ctx.defer()  # ← Должен быть в самом начале

    xml_bytes = await ftp_client.fetch_fields_file()
    statuses = parse_field_statuses(xml_bytes)

    chunks = [statuses[i:i+25] for i in range(0, len(statuses), 25)]

    for i, chunk in enumerate(chunks):
        embed = discord.Embed(
            title=f"🗺️ Статус полей (страница {i+1}/{len(chunks)})" if len(chunks) > 1 else "🗺️ Статус полей",
            color=0x2ecc71
        )
        for line in chunk:
            embed.add_field(name="\u200b", value=line, inline=False)

        await ctx.send(embed=embed)  # Ответ на slash-команду



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
