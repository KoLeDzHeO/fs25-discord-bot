"""Генерация графика онлайна игроков за текущий день."""

from typing import Dict, List
import io

import matplotlib.pyplot as plt


def draw_online_graph(data: Dict[str, List[int]]) -> io.BytesIO:
    """Рисует график онлайна игроков по часам.

    Args:
        data: Словарь {"ник": [24 значения]}.
    Returns:
        BytesIO с PNG-изображением.
    """
    plt.figure(figsize=(10, 4))
    hours = range(24)
    for name, values in data.items():
        plt.plot(hours, values, marker="o", label=name)
    plt.xticks(hours)
    plt.xlabel("Час")
    plt.ylabel("Онлайн")
    plt.title("Онлайн игроков по часам (сегодня)")
    if data:
        plt.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.05, 1))
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="PNG")
    plt.close()
    buf.seek(0)
    return buf
