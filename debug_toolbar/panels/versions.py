import typing as t

from fastapi import Request, Response, __version__

from debug_toolbar.panels import Panel
from debug_toolbar.types import Stats


class VersionsPanel(Panel):
    title = "Versions"
    template = "panels/versions.html"

    @property
    def nav_subtitle(self) -> str:
        return f"FastAPI {__version__}"

    @property
    def scripts(self) -> t.List[str]:
        scripts = super().scripts
        scripts.append(self.url_for("debug_toolbar.static", path="js/versions.js"))
        return scripts

    async def generate_stats(self, request: Request, response: Response) -> Stats:
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
