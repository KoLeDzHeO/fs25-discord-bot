from bot.main import client
from config import config

if __name__ == "__main__":
    client.run(config.DISCORD_TOKEN)
