from contextlib import asynccontextmanager
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import asyncio
import pytest

from utils import weekly_archiver


class FakeConn:
    def __init__(self):
        self.execute_calls = []
        self.executemany_calls = []

    def transaction(self):
        @asynccontextmanager
        async def cm():
            yield
        return cm()

    async def execute(self, query):
        self.execute_calls.append(query)

    async def executemany(self, query, rows):
        self.executemany_calls.append((query, rows))


class FakePool:
    def __init__(self):
        self.conn = FakeConn()

    @asynccontextmanager
    async def acquire(self):
        yield self.conn


def test_fetch_top_rows():
    async def run():
        pool = SimpleNamespace(fetch=AsyncMock(return_value=[{"player_name": "Bob", "hours": 5}, {"player_name": "Alice", "hours": 3}]))
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 8)
        rows = await weekly_archiver._fetch_top_rows(pool, start, end, 10)
        assert rows == [("Bob", 5), ("Alice", 3)]

    asyncio.run(run())


def test_archive_weekly_top_with_rows():
    async def run():
        pool = FakePool()
        fake_rows = [("Bob", 4), ("Alice", 2)]
        with patch.object(weekly_archiver, "_fetch_top_rows", new=AsyncMock(return_value=fake_rows)):
            with patch("utils.weekly_archiver._get_week_bounds", return_value=(datetime(2024, 1, 8), datetime(2024, 1, 15))):
                await weekly_archiver.archive_weekly_top(pool, table_name="test_table", limit=2, max_fetch=5)

        assert len(pool.conn.execute_calls) >= 2
        assert pool.conn.executemany_calls[0][1] == fake_rows[:2]

    asyncio.run(run())


def test_archive_weekly_top_no_rows():
    async def run():
        pool = FakePool()
        with patch.object(weekly_archiver, "_fetch_top_rows", new=AsyncMock(return_value=[])):
            with patch("utils.weekly_archiver._get_week_bounds", return_value=(datetime(2024, 1, 8), datetime(2024, 1, 15))):
                await weekly_archiver.archive_weekly_top(pool, table_name="test_table")

        assert pool.conn.execute_calls == []
        assert pool.conn.executemany_calls == []

    asyncio.run(run())
