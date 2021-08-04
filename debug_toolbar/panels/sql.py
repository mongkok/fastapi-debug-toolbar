import html
import json
import re
import typing as t
from collections import defaultdict

import sqlparse
from fastapi import Request, Response
from sqlparse import tokens as T

from debug_toolbar.panels import Panel
from debug_toolbar.utils import color_generator

__all__ = ["SQLPanel"]


class BoldKeywordFilter:
    def process(
        self,
        stream: t.Generator[t.Tuple[T._TokenType, str], None, None],
    ) -> t.Generator[t.Tuple[t.Type[T.Text], str], None, None]:
        for token_type, value in stream:
            is_keyword = token_type in T.Keyword
            if is_keyword:
                yield T.Text, "<strong>"
            yield token_type, html.escape(value)
            if is_keyword:
                yield T.Text, "</strong>"


def simplify(sql: str) -> str:
    expr = r"SELECT</strong> (...........*?) <strong>FROM"
    sub = r"SELECT</strong> &#8226;&#8226;&#8226; <strong>FROM"
    return re.sub(expr, sub, sql)


def parse_sql(sql: str, aligned_indent: bool = False) -> str:
    stack = sqlparse.engine.FilterStack()
    stack.enable_grouping()

    if aligned_indent:
        stack.stmtprocess.append(
            sqlparse.filters.AlignedIndentFilter(char="&nbsp;", n="<br/>")
        )
    stack.preprocess.append(BoldKeywordFilter())
    stack.postprocess.append(sqlparse.filters.SerializerUnicode())
    return "".join(stack.run(sql))


class SQLPanel(Panel):
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

    def add_query(self, alias: str, query: t.Dict[str, t.Any]) -> None:
        duration = query["duration"]
        sql = query["sql"]

        query.update(
            {
                "duration": duration,
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
        self._queries.append((alias, query))

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
