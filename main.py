"""Запуск Discord-бота."""

import asyncio
import os
import discord
from discord import app_commands

from config.config import (
    config,
    ONLINE_MONTH_GRAPH_TITLE,
)
import asyncpg
from bot.updater import (
    ftp_polling_task,
    api_polling_task,
    save_online_history_task,
    cleanup_old_online_history_task,
)
from utils.online_month_graph import generate_online_month_graph
from utils.logger import log_debug


class MyBot(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


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

        await self.tree.sync()
        log_debug("[Slash] Команды синхронизированы")

    async def on_ready(self):
        log_debug(f"Discord-бот авторизован как {self.user}")

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True

    bot = MyBot(intents=intents)
    tree = bot.tree

    @tree.command(name="online_month", description="График онлайна по дням за последние 30 дней")
    async def online_month_command(interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            path = await generate_online_month_graph(interaction.client.db_pool)
            if not path:
                await interaction.followup.send("Нет данных за последний месяц.")
                return
            embed = discord.Embed(title=ONLINE_MONTH_GRAPH_TITLE)
            embed.set_image(url=f"attachment://{os.path.basename(path)}")
            await interaction.followup.send(
                embed=embed,
                file=discord.File(path, filename=os.path.basename(path)),
            )
        except Exception as e:
            log_debug(f"[CMD] online_month error: {e}")
            await interaction.followup.send(
                "Ошибка при генерации графика.", ephemeral=True
            )

    log_debug("Запускаем Discord-бота")
    try:
        bot.run(config.discord_token)
    finally:
        log_debug("Discord-бот остановлен")

