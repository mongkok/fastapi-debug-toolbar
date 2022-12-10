import re
import typing as t
from urllib import parse

import httpx
from fastapi import status
from fastapi.testclient import TestClient as BaseTestClient

from debug_toolbar.toolbar import DebugToolbar
from debug_toolbar.types import Stats


class TestClient(BaseTestClient):
    def get_store_id(
        self,
        path: str,
        method: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> str:
        response = getattr(self, (method or "get"))(path, **kwargs)

        if response.headers["content-type"].startswith("text/html"):
            return re.findall(r'store-id="(.+?)"', response.content.decode())[0]

        cookie = parse.unquote(response.headers["set-cookie"])
        return re.findall(r'"storeId": "(.+?)"', cookie)[0]

    def render_panel(self, store_id: str, panel_id: str) -> httpx.Response:
        url = self.app.url_path_for("debug_toolbar.render_panel")  # type: ignore
        return self.get(url, params={"store_id": store_id, "panel_id": panel_id})

    def get_stats(self, store_id: str, panel_id: str) -> Stats:
        response = self.render_panel(store_id, panel_id)
        assert response.status_code == status.HTTP_200_OK

        toolbar = DebugToolbar.fetch(store_id)
        assert toolbar
        return toolbar.stats[panel_id]
