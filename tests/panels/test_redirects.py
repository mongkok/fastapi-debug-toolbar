import pytest
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from ..mark import override_panels
from ..testclient import TestClient


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    @app.get(
        "/redirect",
        response_class=RedirectResponse,
        status_code=status.HTTP_302_FOUND,
    )
    async def redirect() -> str:
        return "http://"

    return TestClient(app)


@override_panels(["debug_toolbar.panels.redirects.RedirectsPanel"])
def test_redirects(client: TestClient) -> None:
    headers = {
        "Location": "http://",
    }
    store_id = client.get_store_id("/redirect", headers=headers)
    response = client.render_panel(store_id, "RedirectsPanel")

    assert response.status_code == status.HTTP_200_OK
    assert not response.json()["content"]
