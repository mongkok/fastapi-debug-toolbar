import pytest

from ..mark import override_panels
from ..testclient import TestClient


@pytest.mark.parametrize("path", ["sync", "async"])
@override_panels(["debug_toolbar.panels.profiling.ProfilingPanel"])
def test_profiling(client: TestClient, path: str) -> None:
    store_id = client.get_store_id(f"/{path}")
    stats = client.get_stats(store_id, "ProfilingPanel")

    assert "profileSession" in stats["content"]
