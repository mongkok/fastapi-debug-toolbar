import typing as t

from starlette.requests import Request
from starlette.responses import Response

from debug_toolbar.panels import Panel


class SettingsPanel(Panel):
    title = "Settings"
    template = "panels/settings.html"

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        return {
            "app_settings": {
                **self.toolbar.settings.SETTINGS,
                "Debug Toolbar": self.toolbar.settings,
            },
        }
