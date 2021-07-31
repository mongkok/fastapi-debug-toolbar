import typing as t
from collections import defaultdict
from time import perf_counter

from fastapi import Request, Response
from fastapi.dependencies.utils import (
    is_async_gen_callable,
    is_gen_callable,
    solve_generator,
)
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
        event.listen(
            engine,
            "before_cursor_execute",
            self.before_cursor_execute,
        )
        event.listen(
            engine,
            "after_cursor_execute",
            self.after_cursor_execute,
        )

    def before_cursor_execute(
        self,
        conn: Connection,
        cursor: t.Any,
        statement: str,
        parameters: t.Union[t.Sequence, t.Dict],
        context: DefaultExecutionContext,
        executemany: bool,
    ) -> None:
        context._start_time = perf_counter()

    def after_cursor_execute(
        self,
        conn: Connection,
        cursor: t.Any,
        statement: str,
        parameters: t.Union[t.Sequence, t.Dict],
        context: DefaultExecutionContext,
        executemany: bool,
    ) -> None:
        end_time = perf_counter()
        duration = (end_time - context._start_time) * 1000
        compiled = context.invoked_statement.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)
        alias = str(conn.engine.url)

        query = {
            "statement": statement,
            "params": parameters,
            "start_time": context._start_time,
            "end_time": end_time,
            "duration": duration,
            "sql_raw": sql,
            "sql_formatted": parse_sql(sql, aligned_indent=True),
            "sql_simple": simplify(parse_sql(sql, aligned_indent=False)),
            "is_slow": duration > self.toolbar.settings.SQL_WARNING_THRESHOLD,
            "is_select": sql.lower().strip().startswith("select"),
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
        route = matched_route(request)
        stack = request.scope.get("fastapi_astack")

        if stack is not None and hasattr(route, "dependant"):
            route = t.cast(APIRoute, route)

            for sub_dependant in route.dependant.dependencies:
                call: t.Callable[..., t.Any] = t.cast(
                    t.Callable[..., t.Any], sub_dependant.call
                )
                if is_gen_callable(call) or is_async_gen_callable(call):
                    solved = await solve_generator(
                        call=call,
                        stack=stack,
                        sub_values={},
                    )
                    if isinstance(solved, Session):
                        engine = solved.get_bind()
                        self.register(engine)

        return await super().process_request(request)

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        trace_colors: t.Dict[str, t.Tuple[int, ...]] = defaultdict(
            lambda: next(self._colors)
        )
        query_dups: t.Dict[str, t.Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        query_similar: t.Dict[str, t.Dict[str, t.Any]] = defaultdict(
            lambda: defaultdict(int)
        )
        width_ratio_tally = 0

        for alias, query in self._queries:
            query_dups[alias][query["sql_raw"]] += 1
            query_similar[alias][query["statement"]] += 1
            try:
                width_ratio = (query["duration"] / self._sql_time) * 100
            except ZeroDivisionError:
                width_ratio = 0

            query.update(
                {
                    "trace_color": trace_colors[query["sql_raw"]],
                    "start_offset": width_ratio_tally,
                    "end_offset": width_ratio + width_ratio_tally,
                    "width_ratio": width_ratio,
                }
            )
            width_ratio_tally += width_ratio

        query_dups = {
            alias: {
                query: dup_count
                for query, dup_count in queries.items()
                if dup_count >= 2
            }
            for alias, queries in query_dups.items()
        }
        query_similar = {
            alias: {
                query: (similar_count, next(self._colors))
                for query, similar_count in queries.items()
                if similar_count >= 2
            }
            for alias, queries in query_similar.items()
        }
        for alias, query in self._queries:
            try:
                (query["similar_count"], query["similar_color"]) = query_similar[alias][
                    query["statement"]
                ]
                query["dup_count"] = query_dups[alias][query["sql_raw"]]
            except KeyError:
                continue

        for alias, info in self._databases.items():
            try:
                info["similar_count"] = sum(c for c, _ in query_similar[alias].values())
                info["dup_count"] = sum(c for c in query_dups[alias].values())
            except KeyError:
                continue

        return {
            "databases": self._databases,
            "queries": self._queries,
        }
