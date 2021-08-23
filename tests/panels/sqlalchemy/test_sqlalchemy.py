from ...mark import override_panels, skip_py
from ...testclient import TestClient


@skip_py(3, 7)
@override_panels(["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"])
def test_sqlalchemy(client: TestClient) -> None:
    store_id = client.get_store_id("/sql")
    stats = client.get_stats(store_id, "SQLAlchemyPanel")
    queries = stats["queries"]

    assert len(queries) == 3
    assert queries[0][1]["sql"].startswith("INSERT")
    assert queries[1][1]["dup_count"] == 2
