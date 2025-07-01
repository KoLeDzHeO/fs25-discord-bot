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
    ftp_poll_interval: int = int(os.getenv('FTP_POLL_INTERVAL', 60))
    message_id_file: str = os.getenv('MESSAGE_ID_FILE', 'message_id.json')

config = Config()
