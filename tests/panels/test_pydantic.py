import typing as t

import pytest
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ..mark import override_panels
from ..testclient import TestClient


class Model(BaseModel):
    test: bool


@pytest.fixture
def client(app: FastAPI, get_index: t.Callable) -> TestClient:
    @app.get("/pydantic", response_class=HTMLResponse)
    async def get_pydantic(request: Request, model: Model = Depends()) -> str:
        return get_index(request)

    return TestClient(app)


@override_panels(["debug_toolbar.panels.pydantic.PydanticPanel"])
def test_pydantic(client: TestClient) -> None:
    store_id = client.get_store_id("/pydantic", params={"test": True})
    response = client.render_panel(store_id, "PydanticPanel")

    assert response.status_code == status.HTTP_200_OK
    assert "Model.test" in response.json()["content"]
