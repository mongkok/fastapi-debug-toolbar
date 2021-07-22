import pytest
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from ..decorators import override_panels
from ..templates import Jinja2Templates
from ..testclient import TestClient


@pytest.fixture
def client(app: FastAPI, templates: Jinja2Templates) -> TestClient:
    app.add_middleware(SessionMiddleware, secret_key="")

    @app.get("/session", response_class=HTMLResponse)
    async def get_session(request: Request) -> str:
        request.session["debug"] = True
        return templates.TemplateResponse("index.html", {"request": request})

    return TestClient(app)


@override_panels(["debug_toolbar.panels.request.RequestPanel"])
def test_session(client: TestClient) -> None:
    store_id = client.get_store_id("/session")
    response = client.render_panel(store_id, "RequestPanel")

    assert response.status_code == status.HTTP_200_OK
    assert "debug" in response.json()["content"]
