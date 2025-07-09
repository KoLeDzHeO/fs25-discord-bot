"""Получение файлов по FTP."""

import aioftp
from typing import Optional

from config.config import config
from utils.logger import log_debug

async def fetch_file(file_name: str) -> Optional[str]:
    log_debug(f"[FTP] Пробуем подключиться к {config.ftp_host}:{config.ftp_port} как {config.ftp_user}")
    try:
        async with aioftp.Client.context(
            config.ftp_host,
            config.ftp_port,
            user=config.ftp_user,
            password=config.ftp_pass,
        ) as ftp_client:
            log_debug("[FTP] Заходим в папку profile...")
            await ftp_client.change_directory("profile")
            log_debug("[FTP] Заходим в папку savegame1...")
            await ftp_client.change_directory("savegame1")
            log_debug(f"[FTP] Пробуем скачать файл: {file_name}")
            async with ftp_client.download_stream(file_name) as stream:
                content = await stream.read()
                log_debug(f"[FTP] Файл {file_name} скачан успешно. Размер: {len(content)} байт")
                return content.decode("utf-8")
    except Exception as e:
        log_debug(f"[FTP] ❌ Ошибка загрузки файла '{file_name}': {e}")
        return None

