import typing as t

from starlette.requests import Request
from starlette.responses import Response

from debug_toolbar.panels import Panel


class RequestPanel(Panel):
    title = "Request"
    template = "panels/request.html"

    @property
    def nav_subtitle(self) -> str:
        return self.endpoint.__name__

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        self.endpoint = request.scope["endpoint"]
        stats: t.Dict[str, t.Any] = {"request": request}

        if hasattr(self, "_form"):
            stats["form"] = await request.form()

        if "session" in request.scope:
            stats["session"] = request.session.items()
        return stats
