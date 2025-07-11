"""Entry point for launching the Discord bot."""

import asyncio

import asyncpg
import discord
from discord import app_commands

from config.config import config
from bot.updater import (
    ftp_polling_task,
    api_polling_task,
    save_online_history_task,
    cleanup_old_online_history_task,
)
from utils.total_time_updater import total_time_update_task

from utils.logger import log_debug
from commands.top7lastweek import setup as setup_top7lastweek
from commands.top7week import setup as setup_top7week
from commands.online_month import setup as setup_online_month


class MyBot(discord.Client):
    """Discord bot client with background tasks."""

    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def _ensure_indexes(self) -> None:
        """Create required database indexes if they do not exist."""
        await self.db_pool.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_online_name_date_hour
            ON player_online_history (player_name, date, hour)
            """
        )

    async def setup_hook(self) -> None:
        """Called by discord.py when the client is ready."""
        self.db_pool = await asyncpg.create_pool(dsn=config.postgres_url)
        await self._ensure_indexes()
        asyncio.create_task(api_polling_task())
        asyncio.create_task(ftp_polling_task(self))
        asyncio.create_task(save_online_history_task(self))
        asyncio.create_task(cleanup_old_online_history_task(self))
        asyncio.create_task(total_time_update_task(self))
        log_debug("[SETUP] Background tasks started")

        setup_top7week(self.tree)

        setup_top7lastweek(self.tree)
        await self.tree.sync()
        print("[SYNC] Slash-команды успешно синхронизированы.")
        log_debug("[Slash] Команды синхронизированы")

    async def on_ready(self) -> None:
        """Log successful authorization."""
        log_debug(f"Discord-бот авторизован как {self.user}")

    async def on_message(self, message: discord.Message) -> None:
        """Обрабатывает текстовые сообщения (команды больше не используются)."""
        if message.author.bot:
            return


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True

    bot = MyBot(intents=intents)
    tree = bot.tree

    setup_online_month(tree)

    log_debug("Запускаем Discord-бота")
    try:
        bot.run(config.discord_token)
    finally:
        log_debug("Discord-бот остановлен")
