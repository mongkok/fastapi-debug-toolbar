import re
import typing as t

import requests
from fastapi.testclient import TestClient as BaseTestClient


class TestClient(BaseTestClient):
    def get_store_id(self, path: str, method: str = None, **kwargs: t.Any) -> str:
        response = getattr(self, (method or "get"))(path, **kwargs)
        return re.findall(r'store-id="(.+?)"', response.content.decode())[0]

    def render_panel(self, store_id: str, panel_id: str) -> requests.Response:
        url = self.app.router.url_path_for("debug_toolbar.render_panel")  # type: ignore
        return self.get(f"{url}?store_id={store_id}&panel_id={panel_id}")
