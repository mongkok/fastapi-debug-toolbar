import datetime
import logging
import typing as t

from fastapi import Request, Response
from starlette.concurrency import run_in_threadpool

from debug_toolbar.panels import Panel
from debug_toolbar.types import Stats
from debug_toolbar.utils import is_coroutine, matched_endpoint, pluralize

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
        endpoint = matched_endpoint(request)

        if endpoint is None:
            return await super().process_request(request)

        if is_coroutine(endpoint):
            self.current_thread = threading.current_thread()
        else:
            self.current_thread = await run_in_threadpool(threading.current_thread)

        collector.clear_collection(thread=self.current_thread)
        return await super().process_request(request)

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        records = collector.get_collection(thread=self.current_thread)
        self._records[self.current_thread] = records
        collector.clear_collection(thread=self.current_thread)
        return {"records": records}
