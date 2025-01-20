from __future__ import annotations

from importlib import metadata

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
    def scripts(self) -> list[str]:
        scripts = super().scripts
        scripts.append(self.url_for("debug_toolbar.static", path="js/versions.js"))
        return scripts

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        dists = {d.metadata.get("name", None): d for d in
                 metadata.distributions()}
        packages = sorted(
            dists,
            key=lambda dist: dist.lower() if dist else "",
        )
        return {"packages": packages}
