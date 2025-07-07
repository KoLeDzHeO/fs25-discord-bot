"""Недельный топ активности игроков."""

import asyncpg
from datetime import datetime, timedelta
from typing import List, Tuple

from config.config import config
from utils.helpers import get_moscow_datetime


async def update_player_top_week(db_pool: asyncpg.Pool) -> None:
    """Пересчитывает топ активных игроков за неделю."""
    threshold = config.weekly_top_threshold
    top_size = config.weekly_top_size

    # Текущее московское время
    now = get_moscow_datetime()
    # Находим ближайший прошедший понедельник 12:00
    start = now - timedelta(
        days=now.weekday(),
        hours=now.hour - 12,
        minutes=now.minute,
        seconds=now.second,
        microseconds=now.microsecond,
    )
    if now.hour < 12:
        start -= timedelta(days=7)
    # Конец недели — следующий понедельник 12:00
    end = start + timedelta(days=7)

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT player_name, DATE_TRUNC('hour', check_time) AS hour, COUNT(*) AS cnt
            FROM player_online_history
            WHERE check_time >= $1 AND check_time < $2
            GROUP BY player_name, hour
            HAVING COUNT(*) >= $3
            """,
            start,
            end,
            threshold,
        )

    activity: dict[str, int] = {}
    for r in rows:
        activity[r["player_name"]] = activity.get(r["player_name"], 0) + 1

    top = sorted(activity.items(), key=lambda x: x[1], reverse=True)[:top_size]

    while len(top) < top_size:
        top.append(("-", 0))

    updated_at = get_moscow_datetime()

    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM player_top_week")
        for name, hours in top:
            await conn.execute(
                """
                INSERT INTO player_top_week (player_name, activity_hours, updated_at)
                VALUES ($1, $2, $3)
                """,
                name,
                hours,
                updated_at,
            )


async def get_player_top_week(db_pool: asyncpg.Pool) -> Tuple[List[Tuple[str, int]], datetime]:
    """Возвращает топ-10 игроков и время обновления."""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT player_name, activity_hours, updated_at
            FROM player_top_week
            ORDER BY activity_hours DESC, player_name
            """
        )

    if rows:
        updated_at = rows[0]["updated_at"]
    else:
        updated_at = get_moscow_datetime()

    top = [(r["player_name"], r["activity_hours"]) for r in rows]
    return top, updated_at
