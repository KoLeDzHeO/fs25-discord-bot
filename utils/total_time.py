"""Подсчёт суммарного времени, проведённого игроками на сервере."""

from collections import defaultdict
from typing import Dict

import asyncpg


async def update_player_total_time(db_pool: asyncpg.Pool) -> None:
    """Пересчитывает общее время игры каждого игрока.

    Правила расчёта:
    - таблица ``player_online_history`` содержит фиксации онлайна каждые 15 минут;
    - если в течение часа игрок встретился три раза и более, час засчитывается;
    - в ``player_total_time`` суммируется количество таких часов.
    """

    # Получаем полную статистику по часам для каждого игрока
    async with db_pool.acquire() as conn:
        hourly_rows = await conn.fetch(
            """
            SELECT player_name, DATE_TRUNC('hour', check_time) AS hour, COUNT(*) AS cnt
            FROM player_online_history
            GROUP BY player_name, hour
            HAVING COUNT(*) >= 3
            """
        )

        # Текущие значения общих часов в базе
        existing_rows = await conn.fetch(
            "SELECT player_name, total_hours FROM player_total_time"
        )

    # Считаем зачтённые часы по данным истории
    hours_by_player: Dict[str, int] = defaultdict(int)
    for row in hourly_rows:
        hours_by_player[row["player_name"]] += 1

    current_totals: Dict[str, int] = {
        row["player_name"]: row["total_hours"] for row in existing_rows
    }

    # Вносим обновления только если появилось новое время
    async with db_pool.acquire() as conn:
        for name, total in hours_by_player.items():
            increment = total - current_totals.get(name, 0)
            if increment <= 0:
                continue

            await conn.execute(
                """
                INSERT INTO player_total_time (player_name, total_hours, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (player_name) DO UPDATE
                SET total_hours = player_total_time.total_hours + $2,
                    updated_at = NOW()
                """,
                name,
                increment,
            )

