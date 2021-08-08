import typing as t

from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

from debug_toolbar.types import ServerTiming, Stats
from debug_toolbar.utils import get_name_from_obj

if t.TYPE_CHECKING:
    from debug_toolbar.toolbar import DebugToolbar


class Panel:
    has_content: bool = True

    def __init__(
        self,
        toolbar: "DebugToolbar",
        call_next: RequestResponseEndpoint,
    ) -> None:
        self.toolbar = toolbar
        self.call_next = call_next

    @property
    def panel_id(self) -> str:
        return self.__class__.__name__

    @property
    def enabled(self) -> bool:
        disabled_panels = self.toolbar.settings.DISABLE_PANELS
        panel_path = get_name_from_obj(self)

        disable_panel = (
            panel_path in disabled_panels
            or panel_path.replace(".panel.", ".") in disabled_panels
        )
        if disable_panel:
            default = "off"
        else:
            default = "on"

        return self.toolbar.request.cookies.get(f"dt{self.panel_id}", default) == "on"

    @property
    def nav_title(self) -> str:
        return self.title

    @property
    def nav_subtitle(self) -> str:
        return ""

    @property
    def title(self) -> str:
        raise NotImplementedError

    @property
    def template(self) -> str:
        raise NotImplementedError

    @property
    def content(self) -> str:
        if self.has_content:
            return self.render(**self.get_stats())
        return ""

    def render(self, **context: t.Any) -> str:
        return self.toolbar.render(self.template, **context)

    def url_for(self, name: str, **path_params: t.Any) -> str:
        return self.toolbar.request.url_for(name, **path_params)

    @property
    def scripts(self) -> t.List[str]:
        return []

    async def process_request(self, request: Request) -> Response:
        return await self.call_next(request)

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        pass

    def get_stats(self) -> Stats:
        return self.toolbar.stats.get(self.panel_id, {})

    async def record_stats(self, request: Request, response: Response) -> None:
        stats = await self.generate_stats(request, response)

        if stats is not None:
            self.toolbar.stats.setdefault(self.panel_id, {}).update(stats)

    async def generate_server_timing(
        self,
        request: Request,
        response: Response,
    ) -> ServerTiming:
        pass

    def get_server_timing_stats(self) -> ServerTiming:
        return self.toolbar.server_timing_stats.get(self.panel_id, [])

    async def record_server_timing(self, request: Request, response: Response) -> None:
        stats = await self.generate_server_timing(request, response)

        if stats is not None:
            st_stats = self.toolbar.server_timing_stats.setdefault(self.panel_id, [])
            st_stats += list(stats)
