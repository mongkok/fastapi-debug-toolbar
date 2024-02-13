from fastapi import FastAPI, Request, status

from debug_toolbar.middleware import show_toolbar
from debug_toolbar.settings import DebugToolbarSettings

from .testclient import TestClient


def test_sync(client: TestClient) -> None:
    assert client.get_store_id("/sync")


def test_async(client: TestClient) -> None:
    assert client.get_store_id("/async")


def test_json(client: TestClient) -> None:
    assert client.get_store_id("/openapi.json")


def test_404(client: TestClient) -> None:
    response = client.get("/404")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_show_toolbar_not_allowed(app: FastAPI) -> None:
    scope = {
        "app": app,
        "type": "http",
        "client": ("invalid", 80),
    }
    request = Request(scope=scope)
    settings = DebugToolbarSettings(ALLOWED_HOSTS=["test"])
    assert not show_toolbar(request, settings)
