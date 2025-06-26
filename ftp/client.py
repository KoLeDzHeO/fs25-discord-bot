from typing import Optional
import tempfile

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
            # ``aioftp.Client.download`` expects a filesystem path. Previously we
            # passed a ``BytesIO`` buffer which caused ``open`` to raise an
            # exception like ``expected str, bytes or os.PathLike object, not
            # BytesIO``. To avoid this error we download the file to a temporary
            # location and then read the contents back into memory.
            with tempfile.NamedTemporaryFile() as tmp:
                await ftp.download(path, tmp.name)
                tmp.seek(0)
                return tmp.read()
    except Exception as exc:
        print(f"FTP error: {exc}")
        return None
