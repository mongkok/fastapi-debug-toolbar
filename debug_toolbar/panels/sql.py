import html
import json
import re
import typing as t
from collections import defaultdict

import sqlparse
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from pydantic_extra_types.color import Color
from sqlparse import tokens as T

from debug_toolbar.panels import Panel
from debug_toolbar.types import ServerTiming, Stats
from debug_toolbar.utils import color_generator

__all__ = ["SQLPanel", "parse_sql", "raw_sql"]

Stream = t.Generator[t.Tuple[T._TokenType, str], None, None]


class BoldKeywordFilter:
    def process(self, stream: Stream) -> Stream:
        for token_type, value in stream:
            is_keyword = token_type in T.Keyword
            if is_keyword:
                yield T.Text, "<strong>"
            yield token_type, html.escape(value)
            if is_keyword:
                yield T.Text, "</strong>"


class RawFilter:
    def process(self, stream: Stream) -> Stream:
        for token_type, value in stream:
            if token_type not in T.Number and token_type != T.String.Single:
                yield token_type, value


def simplify(sql: str) -> str:
    expr = r"SELECT</strong> (...........*?) <strong>FROM"
    return re.sub(expr, "SELECT</strong> &#8226;&#8226;&#8226; <strong>FROM", sql)


class FilterStack(sqlparse.engine.FilterStack):
    def run(self, sql: str) -> str:
        self.postprocess.append(sqlparse.filters.SerializerUnicode())
        return "".join(super().run(sql))


def parse_sql(sql: str, aligned_indent: bool = False) -> str:
    stack = FilterStack()

    if aligned_indent:
        stack.enable_grouping()
        stack.stmtprocess.append(
            sqlparse.filters.AlignedIndentFilter(char="&nbsp;", n="<br/>")
        )
    stack.preprocess.append(BoldKeywordFilter())
    return stack.run(sql)


def raw_sql(sql: str) -> str:
    stack = FilterStack()
    stack.preprocess.append(RawFilter())
    return stack.run(sql)


def nqueries(n: int) -> str:
    return f"{n} {'query' if n == 1 else 'queries'}"


class SQLPanel(Panel):
    template = "panels/sql.html"

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._sql_time: float = 0
        self._queries: t.List[t.Tuple[str, t.Dict[str, t.Any]]] = []
        self._databases: t.Dict[str, t.Dict[str, t.Any]] = {}
        self._colors: t.Generator[Color, None, None] = color_generator()

    @property
    def nav_subtitle(self) -> str:
        return f"{nqueries(len(self._queries))} in {self._sql_time:.2f}ms"

    def add_query(self, alias: str, query: t.Dict[str, t.Any]) -> None:
        duration = query["duration"]
        sql = query["sql"]

        query.update(
            {
                "sql_formatted": parse_sql(sql, aligned_indent=True),
                "sql_simple": simplify(parse_sql(sql, aligned_indent=False)),
                "is_slow": duration > self.toolbar.settings.SQL_WARNING_THRESHOLD,
            }
        )
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
        self._queries.append((alias, jsonable_encoder(query)))

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        trace_colors: t.Dict[t.Tuple[str, str], Color] = defaultdict(
            lambda: next(self._colors)
        )
        duplicates: t.Dict[str, t.Dict[t.Tuple[str, str], int]] = defaultdict(
            lambda: defaultdict(int)
        )
        similar: t.Dict[str, t.Dict[str, t.Any]] = defaultdict(lambda: defaultdict(int))
        width_ratio_tally = 0

        def dup_key(query: t.Dict[str, t.Any]) -> t.Tuple[str, str]:
            return (query["sql"], json.dumps(query["params"]))

        def sim_key(query: t.Dict[str, t.Any]) -> str:
            return query.get("raw", query.get("sql"))

        for alias, query in self._queries:
            duplicates[alias][dup_key(query)] += 1
            similar[alias][sim_key(query)] += 1
            try:
                width_ratio = (query["duration"] / self._sql_time) * 100
            except ZeroDivisionError:
                width_ratio = 0

            query.update(
                {
                    "trace_color": trace_colors[dup_key(query)],
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
                query["sim_count"], query["sim_color"] = similar[alias][sim_key(query)]
                query["dup_count"] = duplicates[alias][dup_key(query)]
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
            "sql_time": self._sql_time,
        }

    async def generate_server_timing(
        self,
        request: Request,
        response: Response,
    ) -> ServerTiming:
        stats = self.get_stats()
        n = len(stats.get("queries", []))
        return [("sql", f"SQL {nqueries(n)}", stats.get("sql_time", 0))]
