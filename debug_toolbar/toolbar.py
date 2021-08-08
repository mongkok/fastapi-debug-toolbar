import asyncio
import typing as t
import uuid
from collections import OrderedDict

from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

from debug_toolbar.panels import Panel
from debug_toolbar.settings import DebugToolbarSettings
from debug_toolbar.types import ServerTiming, Stats
from debug_toolbar.utils import get_name_from_obj, import_string

DT = t.TypeVar("DT", bound="DebugToolbar")


class DebugToolbar:
    _store: "OrderedDict[str, DT]" = OrderedDict()  # type: ignore
    _panel_classes: t.Optional[t.Sequence[t.Type[Panel]]] = None

    def __init__(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
        settings: DebugToolbarSettings,
    ) -> None:
        self.request = request
        self.settings = settings
        panels = []

        for panel_class in self.get_panel_classes(
            settings.DEFAULT_PANELS + settings.PANELS,
        )[::-1]:
            panel = panel_class(self, call_next)
            panels.append(panel)

            if panel.enabled:
                call_next = panel.process_request

        self.process_request = call_next
        self._panels = OrderedDict()

        while panels:
            panel = panels.pop()
            self._panels[panel.panel_id] = panel

        self.stats: Stats = {}
        self.server_timing_stats: t.Dict[str, ServerTiming] = {}
        self.store_id: t.Optional[str] = None

    @classmethod
    def get_panel_classes(
        cls: t.Type[DT],
        panels: t.Sequence[str],
    ) -> t.Sequence[t.Type[Panel]]:

        if cls._panel_classes is None:
            cls._panel_classes = [import_string(panel_path) for panel_path in panels]
        return cls._panel_classes

    @property
    def panels(self) -> t.Sequence[Panel]:
        return list(self._panels.values())

    def get_panel_by_id(self, panel_id: str) -> Panel:
        return self._panels[panel_id]

    @property
    def enabled_panels(self) -> t.Sequence[Panel]:
        return [panel for panel in self._panels.values() if panel.enabled]

    def store(self) -> None:
        if self.store_id:
            return

        self.store_id = uuid.uuid4().hex
        self._store[self.store_id] = self

        for _ in range(self.settings.RESULTS_CACHE_SIZE, len(self._store)):
            self._store.popitem(last=False)

    @classmethod
    def fetch(cls: t.Type[DT], store_id: str) -> t.Optional[DT]:
        return cls._store.get(store_id)

    async def record_stats(self, response: Response) -> None:
        tasks = [
            panel.record_stats(self.request, response) for panel in self.enabled_panels
        ]
        await asyncio.gather(*tasks)

    async def record_server_timing(self, response: Response) -> None:
        tasks = [
            panel.record_server_timing(self.request, response)
            for panel in self.enabled_panels
        ]
        await asyncio.gather(*tasks)

    def refresh(self) -> t.Dict[str, t.Any]:
        self.store()
        return {
            "storeId": self.store_id,
            "panels": {
                panel.panel_id: panel.nav_subtitle
                for panel in self.enabled_panels
                if panel.nav_subtitle
            },
        }

    def generate_server_timing_header(self, response: Response) -> None:
        data = []

        for panel in self.enabled_panels:
            stats = panel.get_server_timing_stats()
            if not stats:
                continue
            for key, title, value in stats:
                data.append(f'{panel.panel_id}_{key};dur={value};desc="{title}"')
        if data:
            response.headers["Server-Timing"] = ", ".join(data)

    def render(self, template: str, **context: t.Any) -> str:
        return self.settings.JINJA_ENV.get_template(template).render(
            toolbar=self,
            url_for=self.request.url_for,
            get_name_from_obj=get_name_from_obj,
            **context,
        )

    def render_toolbar(self) -> str:
        self.store()
        return self.render("base.html")
