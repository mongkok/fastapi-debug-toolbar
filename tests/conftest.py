import pytest
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from debug_toolbar.middleware import DebugToolbarMiddleware

from .templates import Jinja2Templates
from .testclient import TestClient


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI(debug=True)
    _app.add_middleware(DebugToolbarMiddleware)
    return _app


@pytest.fixture
def templates() -> Jinja2Templates:
    return Jinja2Templates(directory="tests/templates")


@pytest.fixture
def client(app: FastAPI, templates: Jinja2Templates) -> TestClient:
    @app.get("/sync", response_class=HTMLResponse)
    def get_sync(request: Request) -> str:
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/async", response_class=HTMLResponse)
    async def get_async(request: Request) -> str:
        return templates.TemplateResponse("index.html", {"request": request})

    return TestClient(app)
