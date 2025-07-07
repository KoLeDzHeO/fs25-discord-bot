"""Запуск Discord-бота."""

import asyncio
import discord

from config.config import config
import asyncpg
from bot.updater import ftp_polling_task, api_polling_task, weekly_top_task
from utils.logger import log_debug
from utils.top_week import get_player_top_week
from bot.discord_ui import build_top_week_embed


class MyBot(discord.Client):
    async def setup_hook(self) -> None:
        """Вызывается Discord.py при подготовке клиента."""
        self.db_pool = await asyncpg.create_pool(dsn=config.postgres_url)
        asyncio.create_task(api_polling_task(self.db_pool))
        asyncio.create_task(ftp_polling_task(self, self.db_pool))
        asyncio.create_task(weekly_top_task(self, self.db_pool))

    async def on_ready(self):
        log_debug(f"Discord-бот авторизован как {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if message.content.lower().startswith('/topweek'):
            top, updated_at = await get_player_top_week(self.db_pool)
            embed = build_top_week_embed(top, updated_at)
            await message.channel.send(embed=embed)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True

    bot = MyBot(intents=intents)
    log_debug("Запускаем Discord-бота")
    bot.run(config.discord_token)

