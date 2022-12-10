import logging
import typing as t

import pytest
from fastapi import FastAPI, Request
from fastapi.logger import logger
from fastapi.responses import HTMLResponse

from ..mark import override_panels
from ..testclient import TestClient


@pytest.fixture
def client(app: FastAPI, get_index: t.Callable) -> TestClient:
    @app.get("/log/sync", response_class=HTMLResponse)
    def get_log(request: Request, level: str) -> str:
        logger.log(logging._nameToLevel[level], "")
        return get_index(request)

    @app.get("/log/async", response_class=HTMLResponse)
    async def get_log_async(request: Request, level: str) -> str:
        return get_log(request, level)

    return TestClient(app)


@pytest.mark.parametrize("level", ["ERROR", "WARNING"])
@pytest.mark.parametrize("path", ["sync", "async"])
@override_panels(["debug_toolbar.panels.logging.LoggingPanel"])
def test_logging(client: TestClient, path: str, level: str) -> None:
    store_id = client.get_store_id(f"/log/{path}", params={"level": level})
    stats = client.get_stats(store_id, "LoggingPanel")

    assert stats["records"][0]["level"] == level
