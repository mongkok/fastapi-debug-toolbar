from fastapi import Request, Response

from debug_toolbar.panels import Panel
from debug_toolbar.types import Stats


class RoutesPanel(Panel):
    title = "Routes"
    template = "panels/routes.html"

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        return {
            "routes": request.app.routes,
            "endpoint": request.scope["endpoint"],
        }
