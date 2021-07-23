import typing as t

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from debug_toolbar.middleware import DebugToolbarMiddleware
from debug_toolbar.toolbar import DebugToolbar

from .templates import Jinja2Templates
from .testclient import TestClient


@pytest.fixture
def settings() -> t.Dict[str, t.Any]:
    return {
        "panels": [],
    }


@pytest.fixture
def app(settings: t.Dict[str, t.Any]) -> FastAPI:
    settings.setdefault("disable_panels", [])
    DebugToolbar._panel_classes = None

    _app = FastAPI(debug=True)
    _app.add_middleware(DebugToolbarMiddleware, **settings)
    return _app


@pytest.fixture
def templates() -> Jinja2Templates:
    return Jinja2Templates(directory="tests/templates")


@pytest.fixture
def client(app: FastAPI, templates: Jinja2Templates) -> TestClient:
    @app.get("/sync", response_class=HTMLResponse)
    def get_index(request: Request) -> str:
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/async", response_class=HTMLResponse)
    async def get_async(request: Request) -> str:
        return get_index(request)

    return TestClient(app)
