from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.headers.HeadersPanel"])
def test_headers(client: TestClient) -> None:
    headers = {
        "cookie": "",
    }
    store_id = client.get_store_id("/async", headers=headers)
    stats = client.get_stats(store_id, "HeadersPanel")
    request_headers = stats["request_headers"]

    assert request_headers["cookie"]
