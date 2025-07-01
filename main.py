import discord
import asyncio

from config.config import config
from bot.updater import update_message


class FSBot(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")


def main():
    intents = discord.Intents.default()
    bot = FSBot(intents=intents)
    bot.loop.create_task(update_message(bot))
    bot.run(config.discord_token)


if __name__ == "__main__":
    main()
