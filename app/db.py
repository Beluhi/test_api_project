import os

import asyncpg
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

async def init_db(app: web.Application):
    if "db_pool" in app:
        yield
        return

    pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                phone VARCHAR(30) NOT NULL UNIQUE,
                age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120)
            )
        """)

    app["db_pool"] = pool

    yield

    await pool.close()