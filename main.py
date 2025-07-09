"""Запуск Discord-бота."""

import asyncio
import os
import discord
from discord import app_commands

from config.config import (
    config,
    MONTHLY_GRAPH_OUTPUT_PATH,
    MONTHLY_GRAPH_TITLE,
)
import asyncpg
from bot.updater import (
    ftp_polling_task,
    api_polling_task,
    save_online_history_task,
    cleanup_old_online_history_task,
)
from utils.monthly_online_graph import generate_monthly_online_graph
from utils.logger import log_debug


class MyBot(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    @app_commands.command(name="online_month", description="График активности за 30 дней")
    async def online_month(self, interaction: discord.Interaction) -> None:
        """Отправляет график активности игроков за последний месяц."""
        await interaction.response.defer()
        try:
            path = await generate_monthly_online_graph(self.db_pool)
            embed = discord.Embed(title=MONTHLY_GRAPH_TITLE)
            embed.set_image(url=f"attachment://{os.path.basename(MONTHLY_GRAPH_OUTPUT_PATH)}")
            await interaction.followup.send(
                embed=embed,
                file=discord.File(path, filename=os.path.basename(MONTHLY_GRAPH_OUTPUT_PATH)),
            )
        except Exception as e:
            await interaction.followup.send(f"Ошибка: {e}", ephemeral=True)

    async def _ensure_indexes(self) -> None:
        """Creates required database indexes if they do not exist."""
        await self.db_pool.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_online_name_date_hour
            ON player_online_history (player_name, date, hour)
            """
        )

    async def setup_hook(self) -> None:
        """Вызывается Discord.py при подготовке клиента."""
        self.db_pool = await asyncpg.create_pool(dsn=config.postgres_url)
        await self._ensure_indexes()
        asyncio.create_task(api_polling_task())
        asyncio.create_task(ftp_polling_task(self))
        asyncio.create_task(save_online_history_task(self))
        asyncio.create_task(cleanup_old_online_history_task(self))
        log_debug("[SETUP] Background tasks started")

        self.tree.add_command(self.online_month)

        await self.tree.sync()
        log_debug("[Slash] Команды синхронизированы")

    async def on_ready(self):
        log_debug(f"Discord-бот авторизован как {self.user}")




if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True

    bot = MyBot(intents=intents)
    log_debug("Запускаем Discord-бота")
    try:
        bot.run(config.discord_token)
    finally:
        log_debug("Discord-бот остановлен")

