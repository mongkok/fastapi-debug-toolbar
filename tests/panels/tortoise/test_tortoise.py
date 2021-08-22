from fastapi import status

from ...mark import override_panels
from ...testclient import TestClient


@override_panels(["debug_toolbar.panels.tortoise.TortoisePanel"])
def test_tortoise(client: TestClient) -> None:
    store_id = client.get_store_id("/sql")
    response = client.render_panel(store_id, "TortoisePanel")

    assert response.status_code == status.HTTP_200_OK

    content = response.json()["content"]
    assert "3 queries" in content
    assert "2 similar" in content
    assert "INSERT" in content
    assert "SELECT" in content
