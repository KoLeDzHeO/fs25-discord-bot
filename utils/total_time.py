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
            WHERE player_name <> '' AND player_name <> '-'
            GROUP BY player_name, hour
            HAVING COUNT(*) >= 3
            """
        )



    # Считаем зачтённые часы по данным истории
    hours_by_player: Dict[str, int] = defaultdict(int)
    for row in hourly_rows:
        hours_by_player[row["player_name"]] += 1

    async with db_pool.acquire() as conn:
        for name, total in hours_by_player.items():
            await conn.execute(
                """
                INSERT INTO player_total_time (player_name, total_hours, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (player_name) DO UPDATE
                SET total_hours = EXCLUDED.total_hours,
                    updated_at = NOW()
                """,
                name,
                total,
            )

        await conn.execute(
            "DELETE FROM player_total_time WHERE player_name = '' OR player_name = '-' OR total_hours <= 0"
        )


async def get_player_total_top(db_pool: asyncpg.Pool, limit: int = 50):
    """Возвращает топ игроков по общему времени."""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT player_name, total_hours FROM player_total_time "
            "ORDER BY total_hours DESC LIMIT $1",
            limit,
        )
    return rows
