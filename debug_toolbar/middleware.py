import functools
import json
import re
import typing as t
from urllib import parse

from anyio import CapacityLimiter
from anyio.lowlevel import RunVar
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.routing import NoMatchFound
from starlette.types import ASGIApp

from debug_toolbar.api import render_panel
from debug_toolbar.settings import DebugToolbarSettings
from debug_toolbar.toolbar import DebugToolbar
from debug_toolbar.utils import import_string, matched_route


def show_toolbar(request: Request, settings: DebugToolbarSettings) -> bool:
    if settings.ALLOWED_IPS is not None:
        remote_addr, _ = request["client"]
        return request.app.debug and remote_addr in settings.ALLOWED_IPS
    return request.app.debug


class DebugToolbarMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, **settings: t.Any) -> None:
        super().__init__(app)
        self.settings = DebugToolbarSettings(**settings)
        self.show_toolbar = import_string(self.settings.SHOW_TOOLBAR_CALLBACK)
        self.router: APIRouter = app  # type: ignore[assignment]

        while not isinstance(self.router, APIRouter):
            self.router = self.router.app
        try:
            self.router.url_path_for("debug_toolbar.render_panel")
        except NoMatchFound:
            self.init_toolbar()

    def init_toolbar(self) -> None:
        self.router.get(
            self.settings.API_URL,
            name="debug_toolbar.render_panel",
            include_in_schema=False,
        )(self.require_show_toolbar(render_panel))

        self.router.mount(
            self.settings.STATIC_URL,
            StaticFiles(packages=[__package__]),
            name="debug_toolbar.static",
        )

        @self.router.on_event("startup")
        def set_default_thread_limiter():
            RunVar("_default_thread_limiter").set(CapacityLimiter(1))

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request.scope["route"] = matched_route(request)

        if (
            not request["route"]
            or not self.show_toolbar(request, self.settings)
            or self.settings.API_URL in request.url.path
        ):
            return await call_next(request)

        toolbar = DebugToolbar(request, call_next, self.settings)
        response = t.cast(StreamingResponse, await toolbar.process_request(request))
        content_type = response.headers.get("Content-Type", "")
        is_html = content_type.startswith("text/html")

        if not (is_html or content_type == "application/json") or (
            "gzip" in response.headers.get("Accept-Encoding", "")
        ):
            return response

        await toolbar.record_stats(response)
        await toolbar.record_server_timing(response)
        toolbar.generate_server_timing_header(response)

        if is_html:
            body = b""

            async for chunk in response.body_iterator:
                if not isinstance(chunk, bytes):
                    chunk = chunk.encode(response.charset)
                body += chunk

            decoded = body.decode(response.charset)
            pattern = re.escape(self.settings.INSERT_BEFORE)
            bits = re.split(pattern, decoded, flags=re.IGNORECASE)

            if len(bits) > 1:
                bits[-2] += toolbar.render_toolbar()
                body = self.settings.INSERT_BEFORE.join(bits).encode(response.charset)
                response.headers["Content-Length"] = str(len(body))

            async def stream() -> t.AsyncGenerator[bytes, None]:
                yield body

            response.body_iterator = stream()
        else:
            data = parse.quote(json.dumps(toolbar.refresh()))
            response.set_cookie(key="dtRefresh", value=data)

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
