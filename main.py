"""Запуск Discord-бота."""

import asyncio
import discord
from discord import app_commands

from config.config import config
import asyncpg
from bot.updater import ftp_polling_task, api_polling_task
from utils.logger import log_debug
from utils.total_time import get_player_total_top
from utils.top_week import get_player_top_week
from bot.discord_ui import build_top_week_embed, build_total_top_embed


class MyBot(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """Вызывается Discord.py при подготовке клиента."""
        self.db_pool = await asyncpg.create_pool(dsn=config.postgres_url)
        asyncio.create_task(api_polling_task(self.db_pool))
        asyncio.create_task(ftp_polling_task(self, self.db_pool))
        log_debug("[SETUP] Background tasks started")

        await self.tree.sync()
        log_debug("[Slash] Команды синхронизированы")

    async def on_ready(self):
        log_debug(f"Discord-бот авторизован как {self.user}")


@app_commands.command(name="top7", description="Топ-10 активных игроков за неделю")
async def cmd_top7(interaction: discord.Interaction):
    """Slash-команда для вывода недельного топа игроков."""
    log_debug("[/top7] invoked")
    try:
        await interaction.response.defer(thinking=True)

        top, updated_at = await get_player_top_week(interaction.client.db_pool)
        if not top:
            await interaction.followup.send("Нет данных для отображения", ephemeral=True)
            return

        embed = build_top_week_embed(top[:10], updated_at)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        log_debug(f"[ERROR] /top7: {e}")
        await interaction.followup.send("Произошла ошибка при выполнении команды.", ephemeral=True)


@app_commands.command(name="top", description="Топ-50 по общему времени на сервере")
async def cmd_top(interaction: discord.Interaction):
    """Slash-команда для вывода общего топа игроков."""
    log_debug("[/top] invoked")
    try:
        await interaction.response.defer(thinking=True)

        rows = await get_player_total_top(interaction.client.db_pool, limit=50)
        if not rows:
            await interaction.followup.send("Нет данных для отображения", ephemeral=True)
            return

        top = [(r["player_name"], r["total_hours"]) for r in rows]
        embed = build_total_top_embed(top)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        log_debug(f"[ERROR] /top: {e}")
        await interaction.followup.send("Произошла ошибка при выполнении команды.", ephemeral=True)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True

    bot = MyBot(intents=intents)
    bot.tree.add_command(cmd_top7)
    bot.tree.add_command(cmd_top)
    log_debug("Запускаем Discord-бота")
    try:
        bot.run(config.discord_token)
    finally:
        log_debug("Discord-бот остановлен")

