from typing import Optional
import tempfile

import aioftp
import traceback

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
            # Download the file to a temporary location.
            with tempfile.NamedTemporaryFile() as tmp:
                await ftp.download(path, tmp.name, write_into=True)
                print(f"Downloaded to {tmp.name}")
                tmp.seek(0)
                return tmp.read()
    except Exception as exc:
        print(f"FTP error ({type(exc).__name__}): {exc}")
        traceback.print_exc()
        return None
