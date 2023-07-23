import typing as t
from time import perf_counter

from fastapi import Request, Response

from debug_toolbar.panels import Panel
from debug_toolbar.types import ServerTiming, Stats

try:
    import resource
except ImportError:
    resource = None  # type: ignore[assignment]


class TimerPanel(Panel):
    has_content = resource is not None
    title = "Time"
    template = "panels/timer.html"

    @property
    def nav_subtitle(self) -> str:
        stats = self.get_stats()

        if hasattr(self, "_start_ru"):
            utime = self._end_ru.ru_utime - self._start_ru.ru_utime
            stime = self._end_ru.ru_stime - self._start_ru.ru_stime
            return f"CPU: {(utime + stime) * 1000.0:.2f}ms ({stats['elapsed']:.2f}ms)"

        return f"Total: {stats['elapsed']:.2f}ms"

    @property
    def content(self) -> str:
        stats = self.get_stats()

        rows = (
            ("User CPU time", f"{stats['utime']:.3f} msec"),
            ("System CPU time", f"{stats['stime']:.3f} msec"),
            ("Total CPU time", f"{stats['total']:.3f} msec"),
            ("Elapsed time", f"{stats['elapsed']:.3f} msec"),
            (
                "Context switches",
                f"{stats['vcsw']} voluntary, {stats['ivcsw']} involuntary",
            ),
        )
        return self.render(rows=rows)

    @property
    def scripts(self) -> t.List[str]:
        scripts = super().scripts
        scripts.append(self.url_for("debug_toolbar.static", path="js/timer.js"))
        return scripts

    async def process_request(self, request: Request) -> Response:
        self._start_time = perf_counter()
        if self.has_content:
            self._start_ru = resource.getrusage(resource.RUSAGE_SELF)
        return await super().process_request(request)

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        stats = {
            "elapsed": (perf_counter() - self._start_time) * 1000,
        }
        if hasattr(self, "_start_ru"):
            self._end_ru = resource.getrusage(resource.RUSAGE_SELF)
            utime = 1000 * self._elapsed_ru("ru_utime")
            stime = 1000 * self._elapsed_ru("ru_stime")

            stats.update(
                {
                    "utime": utime,
                    "stime": stime,
                    "total": utime + stime,
                    "vcsw": self._elapsed_ru("ru_nvcsw"),
                    "ivcsw": self._elapsed_ru("ru_nivcsw"),
                }
            )
        return stats

    async def generate_server_timing(
        self,
        request: Request,
        response: Response,
    ) -> ServerTiming:
        stats = self.get_stats()

        return [
            ("utime", "User CPU time", stats.get("utime", 0)),
            ("stime", "System CPU time", stats.get("stime", 0)),
            ("total", "Total CPU time", stats.get("total", 0)),
            ("elapsed", "Elapsed time", stats.get("elapsed", 0)),
        ]

    def _elapsed_ru(self, name: str) -> float:
        return getattr(self._end_ru, name) - getattr(self._start_ru, name)
