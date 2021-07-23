import re

from fastapi import status

from ..mark import override_panels
from ..testclient import TestClient


@override_panels(["debug_toolbar.panels.timer.TimerPanel"])
def test_timer(client: TestClient) -> None:
    store_id = client.get_store_id("/async")
    response = client.render_panel(store_id, "TimerPanel")

    assert response.status_code == status.HTTP_200_OK
    assert re.findall(r"(\d+) msec", response.json()["content"])
