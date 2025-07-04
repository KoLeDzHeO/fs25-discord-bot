import json
from datetime import datetime
import asyncio

import aiofiles
import matplotlib

# Используем неблокирующий backend
matplotlib.use("Agg")
import matplotlib.pyplot as plt


async def update_online_history_hourly(current_online: int, history_file: str = "online_stats.json") -> bool:
    """Сохраняет онлайн раз в час. Возвращает True, если добавлена новая запись."""
    now = datetime.now()
    if now.minute != 0:
        return False
    now_str = now.strftime("%Y-%m-%d %H:00")
    try:
        async with aiofiles.open(history_file, "r", encoding="utf-8") as f:
            content = await f.read()
            history = json.loads(content)
    except Exception:
        history = []
    if history and history[-1].get("time") == now_str:
        return False
    history.append({"time": now_str, "online": current_online})
    if len(history) > 24:
        history = history[-24:]
    async with aiofiles.open(history_file, "w", encoding="utf-8") as f:
        await f.write(json.dumps(history, ensure_ascii=False, indent=2))
    return True


def _plot(times, online, image_file):
    plt.figure(figsize=(8, 3))
    plt.plot(times, online, marker="o")
    plt.title("Онлайн за последние 24 часа (почасовой срез)")
    plt.xlabel("Время")
    plt.ylabel("Игроков онлайн")
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(image_file)
    plt.close()


async def make_online_graph(history_file: str = "online_stats.json", image_file: str = "online_graph.png") -> str | None:
    """Строит график и возвращает путь к файлу, либо None."""
    try:
        async with aiofiles.open(history_file, "r", encoding="utf-8") as f:
            content = await f.read()
            history = json.loads(content)
    except Exception:
        return None
    if not history or len(history) < 2:
        return None
    times = [h["time"][-5:] for h in history]
    online = [h["online"] for h in history]
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _plot, times, online, image_file)
    return image_file
