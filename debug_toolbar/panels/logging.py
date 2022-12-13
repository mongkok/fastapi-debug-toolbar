import datetime
import logging
import typing as t

from fastapi import Request, Response
from starlette.concurrency import run_in_threadpool

from debug_toolbar.panels import Panel
from debug_toolbar.types import Stats
from debug_toolbar.utils import is_coroutine, pluralize

try:
    import threading
except ImportError:
    threading = None  # type: ignore[assignment]


class LogCollector:
    def __init__(self) -> None:
        if threading is None:
            raise NotImplementedError(
                "threading module is not available, "
                "this panel cannot be used without it"
            )
        self.collections: t.Dict[int, t.List[t.Dict[str, t.Any]]] = {}

    def get_collection(
        self,
        thread_id: t.Optional[int] = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        if thread_id is None:
            thread_id = threading.get_ident()
        if thread_id not in self.collections:
            self.collections[thread_id] = []
        return self.collections[thread_id]

    def clear_collection(self, thread_id: t.Optional[int] = None) -> None:
        if thread_id is None:
            thread_id = threading.get_ident()
        if thread_id in self.collections:
            del self.collections[thread_id]

    def collect(
        self,
        item: t.Dict[str, t.Any],
        thread_id: t.Optional[int] = None,
    ) -> None:
        self.get_collection(thread_id).append(item)


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
        if is_coroutine(request["route"].endpoint):
            self.thread_id = threading.get_ident()
        else:
            self.thread_id = await run_in_threadpool(threading.get_ident)

        collector.clear_collection(thread_id=self.thread_id)
        return await super().process_request(request)

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        records = collector.get_collection(thread_id=self.thread_id)
        self._records[self.thread_id] = records
        collector.clear_collection(thread_id=self.thread_id)
        return {"records": records}
