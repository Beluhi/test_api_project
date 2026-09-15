from aiohttp import web

from .db import init_db
from .routes import (
    create_user,
    db_check,
    delete_user,
    get_user,
    list_users,
    update_user,
)

async def health(request: web.Request) -> web.Response:
    return web.json_response(
        {
            "status": "ok",
        }
    )

def create_app() -> web.Application:
    app = web.Application()

    app.router.add_get("/health", health)
    app.router.add_get("/db-check", db_check)

    app.router.add_get("/api/users", list_users)
    app.router.add_get("/api/users/{id}", get_user)
    app.router.add_post("/api/users", create_user)
    app.router.add_patch("/api/users/{id}", update_user)
    app.router.add_delete("/api/users/{id}", delete_user)

    app.cleanup_ctx.append(init_db)

    return app

if __name__ == "__main__":
    web.run_app(
        create_app(),
        host="127.0.0.1",
        port=8080,
    )