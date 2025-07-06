import discord
import asyncio

print("=== [LOG] main.py стартовал ===")

from config.config import config
import asyncpg
from bot.updater import ftp_polling_task, api_polling_task
from bot.logger import log_debug


# Собственный класс клиента, где мы можем запускать фоновые задачи
class MyBot(discord.Client):
    async def setup_hook(self) -> None:
        """Вызывается Discord.py при подготовке клиента."""
        self.db_pool = await asyncpg.create_pool(dsn=config.postgres_url)
        asyncio.create_task(api_polling_task(self.db_pool))
        asyncio.create_task(ftp_polling_task(self, self.db_pool))

    async def on_ready(self):
        # Сообщаем в консоль, что бот успешно авторизовался
        print(f"=== [LOG] Discord-бот авторизован как {self.user} ===")


if __name__ == "__main__":
    # Создаём объект намерений и включаем необходимые события
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True

    # Инициализируем бота и запускаем его
    bot = MyBot(intents=intents)
    print("=== [LOG] Попытка запустить Discord-бота... ===")
    bot.run(config.discord_token)
