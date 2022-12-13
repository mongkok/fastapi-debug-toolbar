import typing as t

from fastapi import Request, Response
from pyinstrument import Profiler
from starlette.concurrency import run_in_threadpool

from debug_toolbar.panels import Panel
from debug_toolbar.types import Stats
from debug_toolbar.utils import is_coroutine


class ProfilingPanel(Panel):
    title = "Profiling"
    template = "panels/profiling.html"

    async def process_request(self, request: Request) -> Response:
        self.profiler = Profiler(**self.toolbar.settings.PROFILER_OPTIONS)
        is_async = is_coroutine(request["route"].endpoint)

        async def call(func: t.Callable) -> None:
            await run_in_threadpool(func) if not is_async else func()

        await call(self.profiler.start)

        try:
            response = await super().process_request(request)
        finally:
            await call(self.profiler.stop)
        return response

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        return {"content": self.profiler.output_html()}
