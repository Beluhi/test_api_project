import asyncpg
from aiohttp import web

def get_pool(request: web.Request) -> asyncpg.Pool:
    return request.app["db_pool"]

# проверка БД
async def db_check(request: web.Request) -> web.Response:
    pool = get_pool(request)
    async with pool.acquire() as conn:
        value = await conn.fetchval("SELECT 1")
    return web.json_response({"status": "ok", "database": "connected", "check_value": value})

# список пользователей
async def list_users(request: web.Request) -> web.Response:
    pool = get_pool(request)
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, surname, phone, age FROM users ORDER BY id")
    return web.json_response({"status": "ok", "data": [dict(row) for row in rows]})

# получение одного пользователя
async def get_user(request: web.Request) -> web.Response:
    user_id = int(request.match_info["id"])
    pool = get_pool(request)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, name, surname, phone, age FROM users WHERE id = $1", user_id)
    if not row:
        return web.json_response({"status": "fail", "reason": "User not found"}, status=404)
    return web.json_response({"status": "ok", "data": dict(row)})

# создание пользователя
async def create_user(request: web.Request) -> web.Response:
    data = await request.json()

    required = ("name", "surname", "phone", "age")
    for field in required:
        if field not in data:
            return web.json_response({"status": "fail", "reason": f"Missing field: {field}"}, status=400)

    name = data.get("name", "")
    surname = data.get("surname", "")
    phone = data.get("phone", "")
    age = data.get("age", 0)

    pool = get_pool(request)
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "INSERT INTO users (name, surname, phone, age) VALUES ($1, $2, $3, $4) RETURNING id, name, surname, phone, age",
                name, surname, phone, age
            )
        except asyncpg.UniqueViolationError:
            return web.json_response({"status": "fail", "reason": "Phone already exists"}, status=409)
    return web.json_response({"status": "ok", "data": dict(row)}, status=201)

# обновление пользователя
async def update_user(request: web.Request) -> web.Response:
    user_id = int(request.match_info["id"])
    data = await request.json()

    fields = {}
    for field in ("name", "surname", "phone", "age"):
        if field in data:
            fields[field] = data[field]

    if not fields:
        return web.json_response({"status": "fail", "reason": "No fields to update"}, status=400)

    set_clauses = [f"{name} = ${i+1}" for i, name in enumerate(fields)]
    params = list(fields.values()) + [user_id]
    query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ${len(params)} RETURNING id, name, surname, phone, age"

    pool = get_pool(request)
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(query, *params)
        except asyncpg.UniqueViolationError:
            return web.json_response({"status": "fail", "reason": "Phone already exists"}, status=409)

    if not row:
        return web.json_response({"status": "fail", "reason": "User not found"}, status=404)

    return web.json_response({"status": "ok", "data": dict(row)})

# удаление пользователя
async def delete_user(request: web.Request) -> web.Response:
    user_id = int(request.match_info["id"])
    pool = get_pool(request)
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)
    if result == "DELETE 0":
        return web.json_response({"status": "fail", "reason": "User not found"}, status=404)
    return web.json_response({"status": "ok", "deleted_id": user_id})