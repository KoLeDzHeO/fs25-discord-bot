"""
Модуль для подключения к FTP-серверу и скачивания XML-файлов.
"""
import aioftp
from typing import Optional

from config.config import config


async def fetch_file(file_name: str) -> Optional[str]:
    """Загружает файл из папки savegame1 на FTP-сервере."""
    path = f"savegame1/{file_name}"
    try:
        async with aioftp.Client.context(
            config.ftp_host,
            config.ftp_port,
            user=config.ftp_user,
            password=config.ftp_pass,
        ) as client:
            async with client.download_stream(path) as stream:
                data = await stream.read()
                return data.decode()
    except Exception as e:
        print(f"\u274c Ошибка загрузки файла '{file_name}': {e}")
        return None
