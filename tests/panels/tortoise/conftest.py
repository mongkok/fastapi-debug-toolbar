import typing as t

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from tortoise import Tortoise

from ...testclient import TestClient
from .crud import create_user, get_user


@pytest.fixture
async def client(
    app: FastAPI,
    get_index: t.Callable,
) -> t.AsyncGenerator[TestClient, None]:
    @app.get("/sql", response_class=HTMLResponse)
    async def get_sql(request: Request) -> str:
        user = await create_user(username="test")
        await get_user(user_id=user.id)
        await get_user(user_id=user.id)
        return get_index(request)

    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["tests.panels.tortoise.models"]},
    )
    await Tortoise.generate_schemas()
    yield TestClient(app)
    await Tortoise.close_connections()
