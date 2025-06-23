import os
import discord
import asyncio
import logging

# Отключаем голосовой клиент, чтобы не вызывался audioop
logging.getLogger("discord.voice_client").disabled = True

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Бот запущен как {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    while True:
        await channel.send("✅ Бот работает. (Тестовое сообщение)")
        await asyncio.sleep(300)  # каждые 5 минут

client.run(TOKEN)
