
import aiosqlite

class DB:
    def __init__(self, path: str):
        self.path = path

    async def execute(self, query: str, params=()):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(query, params)
            await db.commit()

    async def fetchone(self, query: str, params=()):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchone()

    async def fetchall(self, query: str, params=()):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchall()
