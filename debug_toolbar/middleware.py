import functools
import re
import typing as t

from fastapi import HTTPException, status
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import NoMatchFound
from starlette.types import ASGIApp

from debug_toolbar.api import render_panel
from debug_toolbar.settings import DebugToolbarSettings
from debug_toolbar.toolbar import DebugToolbar
from debug_toolbar.utils import import_string


def show_toolbar(request: Request, settings: DebugToolbarSettings) -> bool:
    if settings.ALLOWED_IPS is not None:
        remote_addr, _ = request.scope["client"]
        return request.app.debug and remote_addr in settings.ALLOWED_IPS
    return request.app.debug


class DebugToolbarMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, **settings: t.Any) -> None:
        super().__init__(app)
        self.settings = DebugToolbarSettings(**settings)
        self.show_toolbar = import_string(self.settings.SHOW_TOOLBAR_CALLBACK)

        try:
            app.app.url_path_for(name="debug_toolbar.render_panel")  # type: ignore
        except NoMatchFound:
            self.init_toolbar()

    def init_toolbar(self) -> None:
        self.app.app.get(  # type: ignore
            self.settings.API_URL,
            name="debug_toolbar.render_panel",
        )(self.require_show_toolbar(render_panel))

        self.app.app.mount(  # type: ignore
            self.settings.STATIC_URL,
            StaticFiles(packages=[__package__]),
            name="debug_toolbar.static",
        )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if (
            not self.show_toolbar(request, self.settings)
            or self.settings.STATIC_URL in request.url.path
        ):
            return await call_next(request)

        toolbar = DebugToolbar(request, call_next, self.settings)
        response = await toolbar.process_request(request)
        is_html = response.headers.get("Content-Type", "").startswith("text/html")

        if not is_html or "gzip" in response.headers.get("Accept-Encoding", ""):
            return response

        await toolbar.record_stats(response)
        await toolbar.record_server_timing(response)
        toolbar.generate_server_timing_header(response)

        async for chunk in response.body_iterator:  # type: ignore
            if isinstance(chunk, bytes):
                chunk = chunk.decode(response.charset)

        rendered = toolbar.render_toolbar()
        pattern = re.escape(self.settings.INSERT_BEFORE)
        bits = re.split(pattern, chunk, flags=re.IGNORECASE)

        if len(bits) > 1:
            bits[-2] += rendered
            body = self.settings.INSERT_BEFORE.join(bits).encode(response.charset)

            async def stream() -> t.AsyncGenerator[bytes, None]:
                yield body

            response.headers["Content-Length"] = str(len(body))
            response.body_iterator = stream()  # type: ignore
        return response

    def require_show_toolbar(
        self,
        f: t.Callable[..., t.Any],
    ) -> t.Callable[[t.Any], t.Any]:
        @functools.wraps(f)
        def decorator(request: Request, *args: t.Any, **kwargs: t.Any) -> t.Any:
            if not self.show_toolbar(request, self.settings):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return f(request, *args, **kwargs)

        return decorator
