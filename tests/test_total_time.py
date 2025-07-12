import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


from utils import total_time_updater


class FakeConn:
    def __init__(self):
        self.executemany_calls = []
        self.execute_calls = []

    def transaction(self):
        @asynccontextmanager
        async def cm():
            yield
        return cm()

    async def executemany(self, query, rows):
        self.executemany_calls.append((query, rows))


class FakePool:
    def __init__(self):
        self.conn = FakeConn()

    @asynccontextmanager
    async def acquire(self):
        yield self.conn


def test_fetch_total_hours():
    async def run():
        pool = SimpleNamespace(fetch=AsyncMock(return_value=[{"player_name": "Bob", "hours": 3}]))
        rows = await total_time_updater._fetch_total_hours(pool)
        assert rows == [("Bob", 3)]

    asyncio.run(run())


def test_update_total_time_with_rows():
    async def run():
        pool = FakePool()
        with patch.object(total_time_updater, "_fetch_total_hours", new=AsyncMock(return_value=[("Bob", 2)])):
            await total_time_updater.update_total_time(pool)

        assert len(pool.conn.executemany_calls) == 1
        query, rows = pool.conn.executemany_calls[0]
        assert "INSERT INTO" in query
        assert rows == [("Bob", 2)]

    asyncio.run(run())


def test_update_total_time_no_rows():
    async def run():
        pool = FakePool()
        with patch.object(total_time_updater, "_fetch_total_hours", new=AsyncMock(return_value=[])):
            await total_time_updater.update_total_time(pool)

        assert pool.conn.executemany_calls == []

    asyncio.run(run())
