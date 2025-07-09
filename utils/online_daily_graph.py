"""Генерация суточного графика количества игроков."""

from typing import List
import os
import matplotlib.pyplot as plt

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

    os.makedirs("output", exist_ok=True)
    file_path = "output/online_daily_graph.png"
    plt.savefig(file_path)
    plt.close()
    return file_path
