from __future__ import annotations

import typing as t

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from debug_toolbar.middleware import DebugToolbarMiddleware
from debug_toolbar.toolbar import DebugToolbar

from .testclient import TestClient


@pytest.fixture
def settings() -> dict[str, t.Any]:
    return {}


@pytest.fixture
async def app(settings: dict[str, t.Any]) -> FastAPI:
    settings.setdefault("default_panels", [])
    settings.setdefault("disable_panels", [])
    DebugToolbar._panel_classes = None

    _app = FastAPI(debug=True)
    _app.add_middleware(DebugToolbarMiddleware, **settings)
    return _app


@pytest.fixture
def templates() -> Jinja2Templates:
    return Jinja2Templates(directory="tests/templates")


@pytest.fixture
def get_index(templates: Jinja2Templates) -> t.Callable:
    def func(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(name="index.html", request=request)

    return func


@pytest.fixture
def client(app: FastAPI, get_index: t.Callable) -> TestClient:
    app.get("/sync", response_class=HTMLResponse)(get_index)

    @app.get("/async", response_class=HTMLResponse)
    async def get_async(request: Request) -> HTMLResponse:
        return get_index(request)

    return TestClient(app)
