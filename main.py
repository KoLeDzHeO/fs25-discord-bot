"""Запуск Discord-бота."""

import asyncio
import discord

from config.config import config
import asyncpg
from bot.updater import ftp_polling_task, api_polling_task
from utils.logger import log_debug
from utils.total_time import get_player_total_top
from utils.top_image import draw_top_image


class MyBot(discord.Client):
    async def setup_hook(self) -> None:
        """Вызывается Discord.py при подготовке клиента."""
        self.db_pool = await asyncpg.create_pool(dsn=config.postgres_url)
        asyncio.create_task(api_polling_task(self.db_pool))
        asyncio.create_task(ftp_polling_task(self, self.db_pool))

    async def on_ready(self):
        log_debug(f"Discord-бот авторизован как {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        content = message.content.lower()

        # Команда топа за 7 дней
        if content.startswith('/top7'):
            rows = await self.db_pool.fetch(
                "SELECT player_name, activity_hours FROM player_top_week "
                "ORDER BY activity_hours DESC LIMIT 10"
            )
            img = draw_top_image(list(rows), title='ТОП-10 за неделю', size=10, key='activity_hours')
            file = discord.File(fp=img, filename='top7.png')
            embed = discord.Embed(title='ТОП-10 активных игроков за неделю')
            embed.set_image(url='attachment://top7.png')
            await message.channel.send(embed=embed, file=file)
            return

        # Команда топа за всё время
        if content.startswith('/top'):
            rows = await get_player_total_top(self.db_pool, limit=50)
            img = draw_top_image(list(rows), title='ТОП-50 по общему времени', size=50, key='total_hours')
            file = discord.File(fp=img, filename='top.png')
            embed = discord.Embed(title='ТОП-50 по общему времени на сервере')
            embed.set_image(url='attachment://top.png')
            await message.channel.send(embed=embed, file=file)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True

    bot = MyBot(intents=intents)
    log_debug("Запускаем Discord-бота")
    bot.run(config.discord_token)

