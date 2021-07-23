from fastapi import status

from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.routes.RoutesPanel"])
def test_routes(client: TestClient) -> None:
    store_id = client.get_store_id("/async")
    response = client.render_panel(store_id, "RoutesPanel")

    assert response.status_code == status.HTTP_200_OK
    assert "openapi" in response.json()["content"]
