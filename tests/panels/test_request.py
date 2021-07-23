import pytest
import typing as t

from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from ..decorators import override_panels
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
    response = client.render_panel(store_id, "RequestPanel")

    assert response.status_code == status.HTTP_200_OK
    assert "debug" in response.json()["content"]
