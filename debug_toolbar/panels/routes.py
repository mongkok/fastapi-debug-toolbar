from fastapi import Request, Response

from debug_toolbar.panels import Panel
from debug_toolbar.types import Stats
from debug_toolbar.utils import iter_effective_routes


class RoutesPanel(Panel):
    title = "Routes"
    template = "panels/routes.html"

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        return {
            # Flatten FastAPI >= 0.137 lazy-inclusion nodes so every entry has
            # a real ``.path``/``.methods``/``.endpoint`` for the template.
            "routes": list(iter_effective_routes(request.app.routes)),
            "endpoint": request["endpoint"],
        }
