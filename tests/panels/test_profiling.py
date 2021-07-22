from fastapi import status

from ..decorators import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.profiling.ProfilingPanel"])
def test_profiling(client: TestClient) -> None:
    store_id = client.get_store_id("/async")
    response = client.render_panel(store_id, "ProfilingPanel")

    assert response.status_code == status.HTTP_200_OK
    assert "profileSession" in response.json()["content"]
