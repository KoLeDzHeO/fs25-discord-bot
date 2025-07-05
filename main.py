import discord
import asyncio

print("=== [LOG] main.py стартовал ===")

from config.config import config
from bot.updater import update_message
from bot.logger import log_debug


# Собственный класс клиента, где мы можем запускать фоновые задачи
class MyBot(discord.Client):
    async def setup_hook(self) -> None:
        """Вызывается Discord.py при подготовке клиента."""
        # Запускаем обновление сообщения как отдельную асинхронную задачу
        asyncio.create_task(update_message(self))

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
