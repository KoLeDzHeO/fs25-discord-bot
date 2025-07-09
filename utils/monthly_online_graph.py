"""Генерация графика онлайна игроков за последние 30 дней."""

from __future__ import annotations

from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from config.config import MONTHLY_GRAPH_TITLE
from utils.logger import log_debug


async def generate_monthly_online_graph(db_pool) -> Optional[str]:
    """Создаёт PNG-график активности игроков за месяц.

    Args:
        db_pool: Пул подключений к базе данных.

    Returns:
        Путь к сохранённому изображению.
    """

    try:
        rows = await db_pool.fetch(
            """
            SELECT DATE(check_time) AS date,
                   hour,
                   COUNT(DISTINCT player_name) AS count
            FROM player_online_history
            WHERE check_time >= NOW() - INTERVAL '30 days'
            GROUP BY date, hour
            ORDER BY date, hour
            """
        )
    except Exception as e:
        log_debug(f"[DB] Error fetching monthly online data: {e}")
        raise

    if not rows:
        return None

    data: Dict[str, List[int]] = {}
    for row in rows:
        date_str = row["date"].isoformat()
        hour = int(row["hour"])
        count = row["count"]
        data.setdefault(date_str, [0] * 24)[hour] = count

    # Формируем список дат за последние 30 дней
    today = datetime.utcnow().date()
    start = today - timedelta(days=29)
    dates = [start + timedelta(days=i) for i in range(30)]

    combined: List[int] = []
    for d in dates:
        combined.extend(data.get(d.isoformat(), [0] * 24))

    # Удаляем пустые дни в начале и в конце
    day_data = [data.get(d.isoformat(), [0] * 24) for d in dates]
    first = next((i for i, vals in enumerate(day_data) if any(vals)), 0)
    last = len(day_data) - next(
        (i for i, vals in enumerate(reversed(day_data)) if any(vals)), 1
    )
    dates = dates[first:last]
    day_data = day_data[first:last]
    combined = [val for day in day_data for val in day]

    plt.figure(figsize=(12, 4))
    plt.plot(range(len(combined)), combined, color="tab:blue")

    tick_positions = [i * 24 for i in range(len(dates))]
    tick_labels = [d.strftime("%d.%m") for d in dates]
    plt.xticks(
        ticks=tick_positions,
        labels=tick_labels,
        rotation=90,
        ha="center",
    )
    plt.xlabel("Дата")
    plt.ylabel("Игроки")
    plt.title(MONTHLY_GRAPH_TITLE)

    max_val = max(combined) if combined else 0
    tick_count = max(max_val + 1, 6)
    plt.yticks(range(tick_count))

    plt.grid(axis="both", linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "monthly_online_graph.png")
    plt.savefig(file_path)
    plt.close()

    return file_path

