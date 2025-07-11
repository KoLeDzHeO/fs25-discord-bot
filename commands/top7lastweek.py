from __future__ import annotations

import discord
from discord import app_commands

from asyncpg import Pool

from config.config import WEEKLY_TOP_LIMIT, WEEKLY_TOP_LAST_TABLE
from utils.logger import log_debug


async def _fetch_last_week_top(pool: Pool) -> list[tuple[str, int]]:
    """Fetch archived weekly top rows."""
    try:
        rows = await pool.fetch(
            f"SELECT player_name, hours FROM {WEEKLY_TOP_LAST_TABLE} "
            "ORDER BY hours DESC, player_name LIMIT $1",
            WEEKLY_TOP_LIMIT,
        )
    except Exception as e:
        log_debug(f"[DB] Error fetching last week top: {e}")
        raise

    return [(r["player_name"], int(r["hours"])) for r in rows]


async def _handle_command(interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    pool: Pool = interaction.client.db_pool
    try:
        rows = await _fetch_last_week_top(pool)
    except Exception:
        await interaction.followup.send(
            "Ошибка при получении топа.", ephemeral=True
        )
        return

    if not rows:
        await interaction.followup.send("Нет данных за прошлую неделю.")
        return

    lines = ["ТОП игроков прошлой недели"]
    for idx, (name, hours) in enumerate(rows, start=1):
        lines.append(f"{idx}. {name} — {hours} ч.")

    await interaction.followup.send("\n".join(lines))


def setup(tree: app_commands.CommandTree) -> None:
    @tree.command(name="top7lastweek", description="Топ игроков прошлой недели")
    async def top7lastweek_command(interaction: discord.Interaction) -> None:
        await _handle_command(interaction)

    log_debug("[Slash] Команда /top7lastweek зарегистрирована")

