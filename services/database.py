import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sniper_user:jasdjasjd1221@localhost:5432/currency_sniper")

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None