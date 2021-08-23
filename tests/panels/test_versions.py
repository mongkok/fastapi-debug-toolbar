from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.versions.VersionsPanel"])
def test_versions(client: TestClient) -> None:
    store_id = client.get_store_id("/async")
    stats = client.get_stats(store_id, "VersionsPanel")

    assert stats["packages"]
