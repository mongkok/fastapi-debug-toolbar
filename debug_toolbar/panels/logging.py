import asyncio
import datetime
import logging
import typing as t

from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import Response

from debug_toolbar.panels import Panel
from debug_toolbar.utils import pluralize

try:
    import threading
except ImportError:
    threading = None  # type: ignore


class LogCollector:
    def __init__(self) -> None:
        if threading is None:
            raise NotImplementedError(
                "threading module is not available, "
                "this panel cannot be used without it"
            )
        self.collections: t.Dict[t.Any, t.List[t.Dict[str, t.Any]]] = {}

    def get_collection(self, thread: t.Any = None) -> t.List[t.Dict[str, t.Any]]:
        if thread is None:
            thread = threading.current_thread()
        if thread not in self.collections:
            self.collections[thread] = []
        return self.collections[thread]

    def clear_collection(self, thread: t.Any = None) -> None:
        if thread is None:
            thread = threading.current_thread()
        if thread in self.collections:
            del self.collections[thread]

    def collect(self, item: t.Dict[str, t.Any], thread: t.Any = None) -> None:
        self.get_collection(thread).append(item)


class ThreadTrackingHandler(logging.Handler):
    def __init__(self, collector: LogCollector) -> None:
        logging.Handler.__init__(self)
        self.collector = collector

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = record.getMessage()
        except Exception:
            message = "[Could not get log message]"

        self.collector.collect(
            {
                "message": message,
                "time": datetime.datetime.fromtimestamp(record.created),
                "level": record.levelname,
                "file": record.pathname,
                "line": record.lineno,
                "channel": record.name,
            }
        )


collector = LogCollector()
logging_handler = ThreadTrackingHandler(collector)
logging.root.addHandler(logging_handler)


class LoggingPanel(Panel):
    nav_title = "Logging"
    title = "Log messages"
    template = "panels/logging.html"

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._records: t.Dict[t.Any, t.List[t.Dict[str, t.Any]]] = {}

    @property
    def nav_subtitle(self) -> str:
        stats = self.get_stats()
        record_count = len(stats["records"])
        return f"{record_count} message{pluralize(record_count)}"

    async def process_request(self, request: Request) -> Response:
        collector.clear_collection()
        return await super().process_request(request)

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        if asyncio.iscoroutinefunction(request.scope["endpoint"]):
            current_thread = threading.current_thread()
        else:
            current_thread = await run_in_threadpool(threading.current_thread)

        records = collector.get_collection(thread=current_thread)
        self._records[current_thread] = records
        collector.clear_collection()
        return {"records": records}
