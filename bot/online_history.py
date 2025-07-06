import json
from datetime import datetime, timedelta
import asyncio
from pathlib import Path

import aiofiles
import matplotlib

# Используем неблокирующий backend
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Максимальное количество почасовых записей в истории (31 день)
MAX_HISTORY_RECORDS = 31 * 24


def clean_old_history(history: dict, max_records: int = MAX_HISTORY_RECORDS) -> dict:
    """Удаляет старые записи, оставляя только ``max_records`` последних.

    Порядок ключей соответствует хронологии, поэтому сортировки достаточно,
    чтобы найти самые старые элементы.
    """

    sorted_keys = sorted(history.keys())
    if len(sorted_keys) > max_records:
        keys_to_keep = sorted_keys[-max_records:]
        return {k: history[k] for k in keys_to_keep}
    return history


async def update_online_history(current_players: list[str], history_file: str = "online_history.json") -> bool:
    """Обновляет историю онлайна за месяц.

    При смене месяца архивирует предыдущий ``history_file`` в папку ``history``
    и очищает его. Возвращает ``True``, если данные для текущего часа были
    изменены (добавлены новые ники или создана новая запись)."""

    now = datetime.now()
    hour_key = now.strftime("%Y-%m-%d %H")
    current_month = now.strftime("%Y-%m")

    try:
        async with aiofiles.open(history_file, "r", encoding="utf-8") as f:
            content = await f.read()
            history: dict[str, list[str]] = json.loads(content) if content else {}
    except Exception:
        history = {}

    stored_month = current_month
    if history:
        first_key = next(iter(history))
        stored_month = first_key[:7]

    if stored_month != current_month:
        Path("history").mkdir(exist_ok=True)
        archive_path = Path("history") / f"online_history_{stored_month}.json"
        async with aiofiles.open(archive_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(history, ensure_ascii=False, indent=2))
        history = {}

    old_players = set(history.get(hour_key, []))
    new_players = set(current_players)
    merged_players = sorted(old_players.union(new_players))

    changed = hour_key not in history or merged_players != history.get(hour_key, [])
    history[hour_key] = merged_players

    # Очищаем историю, оставляя только последние записи
    history = clean_old_history(history, MAX_HISTORY_RECORDS)

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

async def make_online_graph(history_file: str = "online_history.json", image_file: str = "online_graph.png") -> str | None:
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
