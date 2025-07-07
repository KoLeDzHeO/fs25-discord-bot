"""Загрузка конфигурации из переменных окружения."""

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
    weekly_top_days: int = int(os.getenv('WEEKLY_TOP_DAYS', 7))
    weekly_top_size: int = int(os.getenv('WEEKLY_TOP_SIZE', 10))
    weekly_top_threshold: int = int(os.getenv('WEEKLY_TOP_THRESHOLD', 3))

config = Config()

