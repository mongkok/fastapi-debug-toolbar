from fastapi import status

from .decorators import override_settings
from .testclient import TestClient


def test_render_panel(client: TestClient) -> None:
    store_id = client.get_store_id("/async")
    response = client.render_panel(store_id=store_id, panel_id="TimerPanel")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["scripts"]


def test_invalid_store_id(client: TestClient) -> None:
    response = client.render_panel(store_id="", panel_id="TimerPanel")

    assert response.status_code == status.HTTP_200_OK
    assert not response.json()["scripts"]


@override_settings(allowed_ips=[])
def test_not_allowed(client: TestClient) -> None:
    response = client.render_panel(store_id="", panel_id="TimerPanel")
    assert response.status_code == status.HTTP_404_NOT_FOUND
