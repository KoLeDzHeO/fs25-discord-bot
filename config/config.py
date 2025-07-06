from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Config:
    discord_token: str = os.getenv('DISCORD_TOKEN')
    channel_id: int = int(os.getenv('DISCORD_CHANNEL_ID', 0))
    api_base_url: str = os.getenv('API_BASE_URL')
    api_secret_code: str = os.getenv('API_SECRET_CODE')
    api_poll_interval: int = int(os.getenv('API_POLL_INTERVAL', 900))
    ftp_poll_interval: int = int(os.getenv('FTP_POLL_INTERVAL', 1800))
    ftp_host: str = os.getenv('FTP_HOST', '')
    ftp_port: int = int(os.getenv('FTP_PORT', 21))
    ftp_user: str = os.getenv('FTP_USER', '')
    ftp_pass: str = os.getenv('FTP_PASS', '')
    postgres_url: str = os.getenv('POSTGRES_URL', '')

config = Config()

print("=== [LOG] Конфиг успешно загружен ===")
print(f"=== [LOG] Канал для публикации: {config.channel_id}")
print(f"=== [LOG] discord_token: {'OK' if config.discord_token else 'None'}")
print(f"=== [LOG] channel_id: {config.channel_id}")
print(f"=== [LOG] ftp_host: {config.ftp_host}")
print(f"=== [LOG] ftp_user: {config.ftp_user}")
print(f"=== [LOG] ftp_port: {config.ftp_port}")
print(f"=== [LOG] api_poll_interval: {config.api_poll_interval}")
print(f"=== [LOG] ftp_poll_interval: {config.ftp_poll_interval}")
print(f"=== [LOG] postgres_url: {bool(config.postgres_url)}")
