from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.routes.RoutesPanel"])
def test_routes(client: TestClient) -> None:
    store_id = client.get_store_id("/async")
    stats = client.get_stats(store_id, "RoutesPanel")

    assert any(route.name == "openapi" for route in stats["routes"])
