import html
import re
import typing as t

import sqlparse
from sqlparse import tokens as T


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
