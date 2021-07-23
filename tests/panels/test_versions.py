from fastapi import status

from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.versions.VersionsPanel"])
def test_versions(client: TestClient) -> None:
    store_id = client.get_store_id("/async")
    response = client.render_panel(store_id, "VersionsPanel")

    assert response.status_code == status.HTTP_200_OK
    assert "fastapi" in response.json()["content"]
