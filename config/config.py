import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

FTP_HOST = os.getenv("FTP_HOST", "")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "")
FTP_PASS = os.getenv("FTP_PASS", "")
FTP_PATH = os.getenv("FTP_PATH", "")

FARM_ID = os.getenv("FARM_ID", "1")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "600"))

DATA_DIR = os.getenv("DATA_DIR", "data")
VEHICLES_FILE = os.getenv("VEHICLES_FILE", "filtered_vehicles.json")
