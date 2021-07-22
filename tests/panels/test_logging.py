import logging

import pytest
from fastapi import FastAPI, Request, status
from fastapi.logger import logger
from fastapi.responses import HTMLResponse

from ..decorators import override_panels
from ..templates import Jinja2Templates
from ..testclient import TestClient


@pytest.fixture
def client(app: FastAPI, templates: Jinja2Templates) -> TestClient:
    @app.get("/log", response_class=HTMLResponse)
    async def get_log(request: Request, level: str) -> str:
        logger.log(logging._nameToLevel[level], "")
        return templates.TemplateResponse("index.html", {"request": request})

    return TestClient(app)


@pytest.mark.parametrize("level", ["ERROR", "WARNING"])
@override_panels(["debug_toolbar.panels.logging.LoggingPanel"])
def test_logging(client: TestClient, level: str) -> None:
    store_id = client.get_store_id(f"/log?level={level}")
    response = client.render_panel(store_id, "LoggingPanel")

    assert response.status_code == status.HTTP_200_OK
    assert level in response.json()["content"]
