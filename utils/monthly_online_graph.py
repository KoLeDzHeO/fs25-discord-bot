"""Генерация графика онлайна игроков за последние 30 дней."""

from __future__ import annotations

from typing import Dict, List
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from config.config import MONTHLY_GRAPH_OUTPUT_PATH, MONTHLY_GRAPH_TITLE


async def generate_monthly_online_graph(db_pool) -> str:
    """Создаёт PNG-график активности игроков за месяц.

    Args:
        db_pool: Пул подключений к базе данных.

    Returns:
        Путь к сохранённому изображению.
    """

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

    plt.figure(figsize=(12, 4))
    plt.plot(range(len(combined)), combined, color="tab:blue")

    tick_positions = [i * 24 for i in range(len(dates))]
    tick_labels = [d.strftime("%d.%m") for d in dates]
    plt.xticks(ticks=tick_positions, labels=tick_labels, rotation=45)
    plt.xlabel("Дата")
    plt.ylabel("Игроки")
    plt.title(MONTHLY_GRAPH_TITLE)

    max_val = max(combined) if combined else 0
    tick_count = max(max_val + 1, 6)
    plt.yticks(range(tick_count))

    plt.grid(axis="both", linestyle="--", alpha=0.5)
    plt.tight_layout()

    os.makedirs(os.path.dirname(MONTHLY_GRAPH_OUTPUT_PATH), exist_ok=True)
    plt.savefig(MONTHLY_GRAPH_OUTPUT_PATH)
    plt.close()

    return MONTHLY_GRAPH_OUTPUT_PATH

