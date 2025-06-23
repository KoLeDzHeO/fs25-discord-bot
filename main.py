import os
import discord
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Бот запущен как {client.user}")
    channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
    channel = client.get_channel(channel_id)
    while True:
        await channel.send("✅ Бот работает. (Тестовое сообщение)")
        await asyncio.sleep(300)  # каждые 5 минут

client.run(TOKEN)
