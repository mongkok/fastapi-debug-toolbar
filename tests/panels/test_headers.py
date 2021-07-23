from fastapi import status

from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.headers.HeadersPanel"])
def test_headers(client: TestClient) -> None:
    store_id = client.get_store_id("/async")
    response = client.render_panel(store_id, "HeadersPanel")

    assert response.status_code == status.HTTP_200_OK
    assert "accept" in response.json()["content"]
