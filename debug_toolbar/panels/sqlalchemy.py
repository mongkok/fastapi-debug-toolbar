import json
import typing as t
from collections import defaultdict
from time import perf_counter

from fastapi import Request, Response
from fastapi.dependencies.utils import solve_dependencies
from fastapi.routing import APIRoute
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.orm import Session

from debug_toolbar.panels import Panel
from debug_toolbar.sql import parse_sql, simplify
from debug_toolbar.utils import color_generator, matched_route


class SQLAlchemyPanel(Panel):
    title = "SQLAlchemy"
    template = "panels/sqlalchemy.html"

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._sql_time: int = 0
        self._queries: t.List[t.Tuple[str, t.Dict[str, t.Any]]] = []
        self._databases: t.Dict[str, t.Dict[str, t.Any]] = {}
        self._colors: t.Generator[t.Tuple[int, ...], None, None] = color_generator()

    @property
    def nav_subtitle(self) -> str:
        count = len(self._queries)
        return (
            f"{count} {'query' if count == 1 else 'queries'}"
            f" in {self._sql_time:.2f}ms"
        )

    def register(self, engine: Engine) -> None:
        event.listen(engine, "before_cursor_execute", self.before_execute)
        event.listen(engine, "after_cursor_execute", self.after_execute)

    def unregister(self, engine: Engine) -> None:
        event.remove(engine, "before_cursor_execute", self.before_execute)
        event.remove(engine, "after_cursor_execute", self.after_execute)

    def before_execute(
        self,
        conn: Connection,
        cursor: t.Any,
        statement: str,
        parameters: t.Union[t.Sequence, t.Dict],
        context: DefaultExecutionContext,
        executemany: bool,
    ) -> None:
        conn.info.setdefault("start_time", []).append(perf_counter())

    def after_execute(
        self,
        conn: Connection,
        cursor: t.Any,
        statement: str,
        parameters: t.Union[t.Sequence, t.Dict],
        context: DefaultExecutionContext,
        executemany: bool,
    ) -> None:
        duration = (perf_counter() - conn.info["start_time"].pop(-1)) * 1000
        alias = str(conn.engine.url)

        query = {
            "sql": statement,
            "params": parameters,
            "duration": duration,
            "sql_formatted": parse_sql(statement, aligned_indent=True),
            "sql_simple": simplify(parse_sql(statement, aligned_indent=False)),
            "is_slow": duration > self.toolbar.settings.SQL_WARNING_THRESHOLD,
            "is_select": context.invoked_statement.is_select,
        }
        if alias not in self._databases:
            self._databases[alias] = {
                "time_spent": duration,
                "num_queries": 1,
                "rgb_color": next(self._colors),
            }
        else:
            self._databases[alias]["time_spent"] += duration
            self._databases[alias]["num_queries"] += 1

        self._sql_time += duration
        self._queries.append((alias, query))

    async def process_request(self, request: Request) -> Response:
        engines: t.List[Engine] = []
        route = matched_route(request)

        if hasattr(route, "dependant"):
            route = t.cast(APIRoute, route)

            solved_result = await solve_dependencies(
                request=request,
                dependant=route.dependant,
                dependency_overrides_provider=route.dependency_overrides_provider,
            )
            for value in solved_result[0].values():
                if isinstance(value, Session):
                    engine = value.get_bind()
                    engines.append(engine)
                    self.register(engine)
        try:
            response = await super().process_request(request)
        finally:
            for engine in engines:
                self.unregister(engine)
        return response

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        trace_colors: t.Dict[t.Tuple[str, str], t.Tuple[int, ...]] = defaultdict(
            lambda: next(self._colors)
        )
        duplicates: t.Dict[str, t.Dict[t.Tuple[str, str], int]] = defaultdict(
            lambda: defaultdict(int)
        )
        similar: t.Dict[str, t.Dict[str, t.Any]] = defaultdict(lambda: defaultdict(int))
        width_ratio_tally = 0

        def query_key(query: t.Dict[str, t.Any]) -> t.Tuple[str, str]:
            return (query["sql"], json.dumps(query["params"]))

        for alias, query in self._queries:
            duplicates[alias][query_key(query)] += 1
            similar[alias][query["sql"]] += 1
            try:
                width_ratio = (query["duration"] / self._sql_time) * 100
            except ZeroDivisionError:
                width_ratio = 0

            query.update(
                {
                    "trace_color": trace_colors[query_key(query)],
                    "start_offset": width_ratio_tally,
                    "end_offset": width_ratio + width_ratio_tally,
                    "width_ratio": width_ratio,
                }
            )
            width_ratio_tally += width_ratio

        duplicates = {
            alias: {query: c for query, c in queries.items() if c > 1}
            for alias, queries in duplicates.items()
        }
        similar = {
            alias: {
                query: (c, next(self._colors)) for query, c in queries.items() if c > 1
            }
            for alias, queries in similar.items()
        }
        for alias, query in self._queries:
            try:
                query["sim_count"], query["sim_color"] = similar[alias][query["sql"]]
                query["dup_count"] = duplicates[alias][query_key(query)]
            except KeyError:
                continue

        for alias, info in self._databases.items():
            try:
                info["sim_count"] = sum(c for c, _ in similar[alias].values())
                info["dup_count"] = sum(c for c in duplicates[alias].values())
            except KeyError:
                continue

        return {
            "databases": self._databases,
            "queries": self._queries,
        }
