"""Вспомогательные функции для работы со временем."""

from datetime import datetime, timedelta

# Смещение часового пояса относительно UTC (Москва по умолчанию)
TIMEZONE_OFFSET = 3


def get_moscow_time() -> str:
    """Возвращает текущее московское время в формате YYYY-MM-DD HH:MM:SS."""
    return (datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def get_moscow_datetime() -> datetime:
    """Возвращает объект datetime с текущим московским временем."""
    return datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)
