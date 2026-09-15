import os
import asyncpg
import pytest_asyncio
from aiohttp.test_utils import TestClient

from app.main import create_app

# фикстура создания соединения с базой и создания тестовой таблицы
@pytest_asyncio.fixture(scope="function")
async def db_pool():
    pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        min_size=1,
        max_size=5,
        command_timeout=10,
    )
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users_test (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                phone VARCHAR(30) NOT NULL UNIQUE,
                age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120)
            )
        """)
    yield pool
    await pool.close()

# фикстура создания приложения
@pytest_asyncio.fixture(scope="function")
async def app(db_pool):
    app = create_app()
    app["db_pool"] = db_pool
    return app

# фикстура создания клиента, который будет отправлять запросы
@pytest_asyncio.fixture(scope="function")
async def client(aiohttp_client, app):
    return await aiohttp_client(app)

# фикстура очистки базы
@pytest_asyncio.fixture(autouse=True)
async def clean_db(db_pool):
    yield
    async with db_pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")