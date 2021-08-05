import typing as t

from fastapi import Request, Response

from debug_toolbar.panels import Panel
from debug_toolbar.types import Stats
from debug_toolbar.utils import get_name_from_obj


class RequestPanel(Panel):
    title = "Request"
    template = "panels/request.html"

    @property
    def nav_subtitle(self) -> str:
        return get_name_from_obj(self.endpoint)

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        self.endpoint = request.scope["endpoint"]
        stats: t.Dict[str, t.Any] = {"request": request}

        if hasattr(self, "_form"):
            stats["form"] = await request.form()

        if "session" in request.scope:
            stats["session"] = request.session.items()
        return stats
