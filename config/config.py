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

config = Config()

# Сколько дней хранить записи об онлайне
cleanup_history_days = 30

# Интервал запуска задачи очистки (в секундах)
cleanup_task_interval_seconds = 86400


# Количество дней для команды /online_month
ONLINE_MONTH_DAYS = 30

# Путь для сохранения графика из /online_month
ONLINE_MONTH_GRAPH_PATH = "output/online_month_graph.png"

# Заголовок для графика из /online_month
ONLINE_MONTH_GRAPH_TITLE = "Онлайн по дням (последние 30 дней)"

