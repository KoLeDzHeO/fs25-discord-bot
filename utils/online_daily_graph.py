"""Генерация суточного графика количества игроков."""

from datetime import timedelta
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt

from config.config import (
    ONLINE_DAILY_GRAPH_PATH,
    ONLINE_DAILY_GRAPH_TITLE,
)
from utils.helpers import get_moscow_datetime
from utils.logger import log_debug


async def fetch_daily_online_counts(db_pool) -> List[int]:
    """Возвращает число уникальных игроков по часам за текущие сутки."""

    start = get_moscow_datetime().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    try:
        rows = await db_pool.fetch(
            """
            SELECT EXTRACT(HOUR FROM check_time) AS hour,
                   COUNT(DISTINCT player_name) AS count
            FROM player_online_history
            WHERE check_time BETWEEN $1 AND $2
            GROUP BY hour
            ORDER BY hour
            """,
            start,
            end,
        )
    except Exception as e:
        log_debug(f"[DB] Error fetching online day data: {e}")
        raise

    counts = [0] * 24
    for row in rows:
        counts[int(row["hour"])] = row["count"]

    return counts


def save_daily_online_graph(counts: List[int]) -> str:
    """Сохраняет PNG-график количества игроков по часам за сегодня."""

    now_hour = get_moscow_datetime().hour
    hours = list(range(now_hour + 1, 24)) + list(range(0, now_hour + 1))
    rotated = counts[now_hour + 1 :] + counts[: now_hour + 1]

    plt.figure(figsize=(10, 3))
    plt.bar(range(len(rotated)), rotated, color="tab:blue")

    plt.xticks(ticks=range(len(hours)), labels=hours)
    plt.xlim(-0.5, len(hours) - 0.5)

    plt.xlabel("Час")
    plt.ylabel("Игроки")
    plt.title(ONLINE_DAILY_GRAPH_TITLE)

    max_val = max(rotated) if rotated else 0
    tick_count = max(max_val + 1, 6)
    plt.yticks(range(tick_count))

    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_path = Path(ONLINE_DAILY_GRAPH_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    return str(output_path)
