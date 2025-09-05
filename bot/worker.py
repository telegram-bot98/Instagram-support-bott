
import asyncio

class Worker:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._running = False

    async def run(self, bot):
        # Worker بسيط يشتغل بالخلفية (تقدر توسّعه لاحقًا)
        self._running = True
        while self._running:
            await asyncio.sleep(10)
