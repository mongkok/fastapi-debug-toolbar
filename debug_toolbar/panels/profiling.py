import asyncio
import typing as t

from pyinstrument import Profiler
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match

from debug_toolbar.panels import Panel


def is_async_endpoint(request: Request) -> bool:
    for route in request.app.routes:
        match, child_scope = route.matches(request.scope)
        if match == Match.FULL:
            return asyncio.iscoroutinefunction(route.endpoint)
    return True


async def call_profiler(func: t.Callable, is_async: bool) -> None:
    if not is_async:
        await run_in_threadpool(func)
    else:
        func()


class ProfilingPanel(Panel):
    title = "Profiling"
    template = "panels/profiling.html"

    async def process_request(self, request: Request) -> Response:
        self.profiler = Profiler(**self.toolbar.settings.PROFILER_OPTIONS)
        is_async = is_async_endpoint(request)

        await call_profiler(self.profiler.start, is_async)
        response = await super().process_request(request)
        await call_profiler(self.profiler.stop, is_async)
        return response

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        return {"content": self.profiler.output_html()}
