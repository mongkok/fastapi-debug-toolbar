import pytest

from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.settings.SettingsPanel"])
def test_settings(client: TestClient) -> None:
    store_id = client.get_store_id("/async")

    with pytest.raises(KeyError):
        client.get_stats(store_id, "SettingsPanel")
