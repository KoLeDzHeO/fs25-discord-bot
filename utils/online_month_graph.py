"""Генерация графика уникальных игроков по дням за последние N дней."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional, List

import matplotlib.pyplot as plt

from config.config import (
    ONLINE_MONTH_DAYS,
    ONLINE_MONTH_GRAPH_PATH,
    ONLINE_MONTH_GRAPH_TITLE,
)
from utils.logger import log_debug


def save_monthly_online_graph(dates: List[str], counts: List[int]) -> str:
    """Сохраняет PNG-график уникальных игроков по дням."""

    plt.figure(figsize=(10, 4))
    plt.bar(range(len(counts)), counts, color="tab:blue")

    plt.xticks(ticks=range(len(dates)), labels=dates)
    plt.xlim(-0.5, len(dates) - 0.5)

    plt.xlabel("Дата")
    plt.ylabel("Уникальные игроки")
    plt.title(ONLINE_MONTH_GRAPH_TITLE)

    max_val = max(counts) if counts else 0
    tick_count = max(max_val + 1, 6)
    plt.yticks(range(tick_count))

    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_path = os.path.join(os.getcwd(), ONLINE_MONTH_GRAPH_PATH)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()

    return output_path


async def generate_online_month_graph(db_pool) -> Optional[str]:
    """Создаёт PNG-график уникальных игроков по дням.

    Args:
        db_pool: Пул подключений к базе данных.

    Returns:
        Путь к сохранённому изображению или ``None`` при отсутствии данных.
    """

    try:
        rows = await db_pool.fetch(
            f"""
            SELECT DATE(check_time) AS day,
                   COUNT(DISTINCT player_name) AS count
            FROM player_online_history
            WHERE check_time >= NOW() - INTERVAL '{ONLINE_MONTH_DAYS} days'
            GROUP BY day
            ORDER BY day
            """
        )
    except Exception as e:
        log_debug(f"[DB] Error fetching online month data: {e}")
        raise

    if not rows:
        return None

    counts = {row["day"]: row["count"] for row in rows}

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=ONLINE_MONTH_DAYS - 1)
    dates = [start_date + timedelta(days=i) for i in range(ONLINE_MONTH_DAYS)]
    values = [counts.get(d, 0) for d in dates]

    try:
        tick_labels = [d.strftime("%d.%m") for d in dates]
        return save_monthly_online_graph(tick_labels, values)
    except Exception as e:
        log_debug(f"[GRAPH] Error building online month graph: {e}")
        raise
