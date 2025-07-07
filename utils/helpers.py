from datetime import datetime, timedelta


def get_moscow_time() -> str:
    """Возвращает текущее московское время в формате YYYY-MM-DD HH:MM:SS."""
    return (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")


def get_moscow_datetime() -> datetime:
    """Возвращает объект datetime с текущим московским временем."""
    return datetime.utcnow() + timedelta(hours=3)
