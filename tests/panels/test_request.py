import typing as t

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from ..mark import override_panels
from ..testclient import TestClient


@pytest.fixture
def client(app: FastAPI, get_index: t.Callable) -> TestClient:
    app.add_middleware(SessionMiddleware, secret_key="")

    @app.get("/session", response_class=HTMLResponse)
    async def get_session(request: Request) -> str:
        request.session["debug"] = True
        return get_index(request)

    return TestClient(app)


@override_panels(["debug_toolbar.panels.request.RequestPanel"])
def test_session(client: TestClient) -> None:
    store_id = client.get_store_id("/session")
    stats = client.get_stats(store_id, "RequestPanel")

    assert stats["session"]["debug"]
