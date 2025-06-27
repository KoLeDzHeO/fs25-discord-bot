import os


def _get_env(name: str, default: str = "") -> str:
    """Return an environment variable without surrounding quotes."""
    value = os.getenv(name, default).strip()
    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {'"', "'"}
    ):
        return value[1:-1]
    return value


DISCORD_TOKEN = _get_env("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(_get_env("DISCORD_CHANNEL_ID", "0"))

FTP_HOST = _get_env("FTP_HOST")
FTP_PORT = int(_get_env("FTP_PORT", "21"))
FTP_USER = _get_env("FTP_USER")
FTP_PASS = _get_env("FTP_PASS")
FTP_PATH = _get_env("FTP_PATH")
FTP_PATH_FIELDS = _get_env("FTP_PATH_FIELDS")

FARM_ID = os.getenv("FARM_ID", "1")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "600"))

DATA_DIR = os.getenv("DATA_DIR", "data")
VEHICLES_FILE = os.getenv("VEHICLES_FILE", "filtered_vehicles.json")
