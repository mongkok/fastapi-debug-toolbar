from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.pydantic.PydanticPanel"])
def test_pydantic(client: TestClient) -> None:
    store_id = client.get_store_id("/openapi.json")
    stats = client.get_stats(store_id, "PydanticPanel")

    assert stats["validations"]
