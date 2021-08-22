from fastapi import status

from ...mark import override_panels, skip_py36
from ...testclient import TestClient


@skip_py36
@override_panels(["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"])
def test_sqlalchemy(client: TestClient) -> None:
    store_id = client.get_store_id("/sql")
    response = client.render_panel(store_id, "SQLAlchemyPanel")

    assert response.status_code == status.HTTP_200_OK

    content = response.json()["content"]
    assert "3 queries" in content
    assert "2 similar" in content
    assert "INSERT" in content
    assert "SELECT" in content
