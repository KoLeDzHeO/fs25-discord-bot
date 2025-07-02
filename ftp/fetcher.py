"""Модуль для подключения к FTP-серверу и скачивания XML-файлов."""

import aioftp
from typing import Optional

from config.config import config


async def fetch_file(file_name: str) -> Optional[str]:
    """Загружает указанный XML-файл из папки ``savegame1``."""

    # Формируем полный путь к файлу на FTP-сервере
    path = f"savegame1/{file_name}"

    try:
        # Подключаемся к FTP и скачиваем файл
        async with aioftp.Client.context(
            config.ftp_host,
            config.ftp_port,
            user=config.ftp_user,
            password=config.ftp_pass,
        ) as ftp_client:
            async with ftp_client.download_stream(path) as stream:
                content = await stream.read()
                # Возвращаем XML в виде строки
                return content.decode("utf-8")
    except Exception as e:
        # Ошибки выводим в консоль и возвращаем None
        print(f"\u274c Ошибка загрузки файла '{file_name}': {e}")
        return None
