"""Entry point for launching the Discord bot."""

import asyncio
import os

import asyncpg
import discord
from discord import app_commands

from config.config import config, ONLINE_MONTH_GRAPH_TITLE
from bot.updater import (
    ftp_polling_task,
    api_polling_task,
    save_online_history_task,
    cleanup_old_online_history_task,
)
from utils.online_month_graph import generate_online_month_graph
from utils.weekly_top import generate_weekly_top
from utils.logger import log_debug
from commands.top7lastweek import setup as setup_top7lastweek


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
        log_debug("[SETUP] Background tasks started")

        @self.tree.command(
            name="top7week",
            description="Топ 7 игроков за неделю по часам",
        )
        async def top7week_command(
            interaction: discord.Interaction,
        ) -> None:
            """Handle `/top7week` command."""
            await interaction.response.defer()
            try:
                text = await generate_weekly_top(interaction.client.db_pool)
                await interaction.followup.send(text)
            except Exception as e:
                log_debug(f"[CMD] top7week error: {e}")
                await interaction.followup.send(
                    "Ошибка при получении топа.", ephemeral=True
                )

        log_debug("[Slash] Команда /top7week зарегистрирована")

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

    @tree.command(name="online_month", description="График онлайна по дням за последние 30 дней")
    async def online_month_command(interaction: discord.Interaction) -> None:
        """Handle `/online_month` command."""
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
