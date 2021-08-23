from ...mark import override_panels
from ...testclient import TestClient


@override_panels(["debug_toolbar.panels.tortoise.TortoisePanel"])
def test_tortoise(client: TestClient) -> None:
    store_id = client.get_store_id("/sql")
    stats = client.get_stats(store_id, "TortoisePanel")
    queries = stats["queries"]

    assert len(queries) == 3
    assert queries[0][1]["sql"].startswith("INSERT")
    assert queries[1][1]["dup_count"] == 2
