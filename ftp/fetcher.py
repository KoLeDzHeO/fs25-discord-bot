"""Модуль для подключения к FTP-серверу и скачивания XML-файлов."""

import aioftp
from typing import Optional

from config.config import config


async def fetch_file(file_name: str) -> Optional[str]:
    """Загружает указанный XML-файл из папки ``savegame1``."""

    try:
        # Подключаемся к FTP-серверу
        async with aioftp.Client.context(
            config.ftp_host,
            config.ftp_port,
            user=config.ftp_user,
            password=config.ftp_pass,
        ) as ftp_client:
            # Переходим в нужную директорию
            await ftp_client.change_directory("savegame1")

            # Загружаем файл из неё
            async with ftp_client.download_stream(file_name) as stream:
                content = await stream.read()
                return content.decode("utf-8")

    except Exception as e:
        print(f"❌ Ошибка загрузки файла '{file_name}': {e}")
        return None
