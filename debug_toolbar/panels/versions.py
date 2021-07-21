import typing as t

import fastapi
from starlette.requests import Request
from starlette.responses import Response

from debug_toolbar.panels import Panel


class VersionsPanel(Panel):
    title = "Versions"
    template = "panels/versions.html"

    @property
    def nav_subtitle(self) -> str:
        return f"FastAPI {fastapi.__version__}"

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        try:
            import pkg_resources
        except ImportError:
            packages = []
        else:
            packages = sorted(
                pkg_resources.working_set,
                key=lambda pkg: pkg.project_name.lower(),
            )
        return {"packages": packages}
