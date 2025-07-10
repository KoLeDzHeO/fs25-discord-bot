"""Генерация суточного графика количества игроков."""

from pathlib import Path
from typing import List

import matplotlib.pyplot as plt

from config.config import ONLINE_DAILY_GRAPH_PATH
from utils.helpers import get_moscow_datetime


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
    plt.title("Количество игроков по часам (сегодня)")

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
