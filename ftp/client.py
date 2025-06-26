from typing import Optional
import tempfile
import traceback

import aioftp

from config import config


async def fetch_file(path: str) -> Optional[bytes]:
    """Download a file from the configured FTP server."""
    print(
        "Connecting to FTP",
        f"host={config.FTP_HOST}",
        f"port={config.FTP_PORT}",
        f"user={config.FTP_USER}",
    )
    try:
        async with aioftp.Client.context(
            config.FTP_HOST,
            config.FTP_PORT,
            config.FTP_USER,
            config.FTP_PASS,
        ) as ftp:
            print(f"Connected. Downloading {path}")
            # ``aioftp.Client.download`` expects a filesystem path. Previously we
            # passed a ``BytesIO`` buffer which caused ``open`` to raise an
            # exception like ``expected str, bytes or os.PathLike object, not
            # BytesIO``. To avoid this error we download the file to a temporary
            # location and then read the contents back into memory.
            with tempfile.NamedTemporaryFile() as tmp:
                await ftp.download(path, tmp.name)
                print(f"Downloaded to {tmp.name}")
                tmp.seek(0)
                data = tmp.read()
                print(f"Read {len(data)} bytes")
                return data
    except Exception as exc:
        print(f"FTP error: {exc}")
        traceback.print_exc()
        return None
