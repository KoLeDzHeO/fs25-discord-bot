"""Запуск Discord-бота."""

import asyncio
import discord
from discord import app_commands

from config.config import config
import asyncpg
from bot.updater import ftp_polling_task, api_polling_task
from utils.logger import log_debug
from utils.total_time import get_player_total_top
from utils.top_image import draw_top_image


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
        rows = await interaction.client.db_pool.fetch(
            "SELECT player_name, activity_hours FROM player_top_week ORDER BY activity_hours DESC LIMIT 10"
        )
        if not rows:
            await interaction.followup.send("Данных нет", ephemeral=True)
            return
        try:
            img = draw_top_image(list(rows), title="ТОП-10 за неделю", size=10, key="activity_hours")
            file = discord.File(fp=img, filename="top7.png")
            embed = discord.Embed(title="ТОП-10 активных игроков за неделю")
            embed.set_image(url="attachment://top7.png")
            await interaction.followup.send(embed=embed, file=file)
        except Exception:
            lines = [f"{i+1}. {row['player_name']} - {row['activity_hours']} ч" for i, row in enumerate(rows)]
            text = "\n".join(lines)
            await interaction.followup.send(
                f"Не удалось сгенерировать картинку, вот текстовый топ:\n{text}",
                ephemeral=True,
            )
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
            await interaction.followup.send("Данных нет", ephemeral=True)
            return
        try:
            img = draw_top_image(list(rows), title="ТОП-50 по общему времени", size=50, key="total_hours")
            file = discord.File(fp=img, filename="top.png")
            embed = discord.Embed(title="ТОП-50 по общему времени на сервере")
            embed.set_image(url="attachment://top.png")
            await interaction.followup.send(embed=embed, file=file)
        except Exception:
            lines = [f"{i+1}. {row['player_name']} - {row['total_hours']} ч" for i, row in enumerate(rows)]
            text = "\n".join(lines)
            await interaction.followup.send(
                f"Не удалось сгенерировать картинку, вот текстовый топ:\n{text}",
                ephemeral=True,
            )
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

