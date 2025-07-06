import asyncio
from datetime import datetime, timedelta

import asyncpg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


async def insert_online_players(db_pool: asyncpg.Pool, players: list[str]) -> None:
    """Сохраняет онлайн игроков в таблицу ``player_online_history``."""
    now = datetime.now()
    slot_start = now - timedelta(
        minutes=now.minute % 15, seconds=now.second, microseconds=now.microsecond
    )
    async with db_pool.acquire() as conn:
        for player in players:
            await conn.execute(
                """
                INSERT INTO player_online_history (player_name, check_time)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
                """,
                player,
                slot_start,
            )


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
    ax.set_xlim(0, len(times) - 1)
    ymax = max(online) if online else 0
    ax.set_ylim(bottom=0, top=max(5, ymax))
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(image_file)
    plt.close()


async def make_online_graph(db_pool: asyncpg.Pool, image_file: str = "online_graph.png") -> str:
    """Строит график по данным из PostgreSQL."""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT DATE_TRUNC('hour', check_time) AS hour,
                   COUNT(DISTINCT player_name) AS cnt
            FROM player_online_history
            WHERE check_time >= NOW() - INTERVAL '24 hour'
            GROUP BY hour
            ORDER BY hour
            """
        )

    data = {r["hour"].replace(minute=0, second=0, microsecond=0): r["cnt"] for r in rows}
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    times = []
    online = []
    for i in range(23, -1, -1):
        point_time = now - timedelta(hours=i)
        times.append(point_time.strftime("%H:00"))
        online.append(data.get(point_time, 0))

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _plot, times, online, image_file)
    return image_file
