from io import BytesIO
from typing import Optional

import aioftp

from config import config


async def fetch_file(path: str) -> Optional[bytes]:
    """Download a file from the configured FTP server."""
    try:
        async with aioftp.Client.context(
            config.FTP_HOST,
            config.FTP_PORT,
            config.FTP_USER,
            config.FTP_PASS,
        ) as ftp:
            buffer = BytesIO()
            await ftp.download(path, buffer)
            return buffer.getvalue()
    except Exception as exc:
        print(f"FTP error: {exc}")
        return None
