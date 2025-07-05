import json
from datetime import datetime, timedelta
import asyncio

import aiofiles
import matplotlib

# Используем неблокирующий backend
matplotlib.use("Agg")
import matplotlib.pyplot as plt


async def update_online_history(current_players: list[str], history_file: str = "online_stats.json") -> bool:
    """Сохраняет список уникальных ников для текущего часа.

    Возвращает ``True``, если данные для часа были изменены (добавлены новые
    ники или создана новая запись)."""

    hour_key = datetime.now().strftime("%Y-%m-%d %H")

    try:
        async with aiofiles.open(history_file, "r", encoding="utf-8") as f:
            content = await f.read()
            history: dict[str, list[str]] = json.loads(content)
    except Exception:
        history = {}

    old_players = set(history.get(hour_key, []))
    new_players = set(current_players)
    merged_players = sorted(old_players.union(new_players))

    changed = hour_key not in history or merged_players != history.get(hour_key, [])
    history[hour_key] = merged_players

    # Оставляем только последние 24 часа
    last_hours = sorted(history.keys())[-24:]
    history = {h: history[h] for h in last_hours}

    async with aiofiles.open(history_file, "w", encoding="utf-8") as f:
        await f.write(json.dumps(history, ensure_ascii=False, indent=2))

    return changed


from matplotlib.ticker import MaxNLocator


def _plot(times, online, image_file):
    plt.figure(figsize=(9, 3))
    ax = plt.gca()
    ax.plot(range(len(times)), online, marker="o")
    ax.set_title("Онлайн за последние 24 часа (почасовой срез)")
    ax.set_xlabel("Время")
    ax.set_ylabel("Игроков онлайн")
    ax.set_xticks(range(len(times)))
    ax.set_xticklabels(times, rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    
    # ГЛАВНОЕ ДОБАВЛЕНИЕ — фиксируем X от 0 до N-1
    ax.set_xlim(0, len(times) - 1)
    
    # ВСЕГДА показываем минимум 5 делений по Y
    ymax = max(online)
    ax.set_ylim(bottom=0, top=max(5, ymax))
    
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(image_file)
    plt.close()

async def make_online_graph(history_file: str = "online_stats.json", image_file: str = "online_graph.png") -> str | None:
    """Строит график и возвращает путь к файлу, либо None."""
    try:
        async with aiofiles.open(history_file, "r", encoding="utf-8") as f:
            content = await f.read()
            history: dict[str, list[str]] = json.loads(content)
    except Exception:
        history = {}

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    times = []
    online = []
    for i in range(23, -1, -1):
        point_time = now - timedelta(hours=i)
        key = point_time.strftime("%Y-%m-%d %H")
        times.append(point_time.strftime("%H:00"))
        online.append(len(history.get(key, [])))

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _plot, times, online, image_file)
    return image_file
