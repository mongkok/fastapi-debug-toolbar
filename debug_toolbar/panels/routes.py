import typing as t

from fastapi import Request, Response

from debug_toolbar.panels import Panel


class RoutesPanel(Panel):
    title = "Routes"
    template = "panels/routes.html"

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        return {
            "routes": request.app.routes,
            "endpoint": request.scope["endpoint"],
        }
