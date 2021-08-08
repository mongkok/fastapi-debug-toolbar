import typing as t
from time import perf_counter

from fastapi import Request, Response
from fastapi.dependencies.utils import solve_dependencies
from fastapi.routing import APIRoute
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.orm import Session

from debug_toolbar.panels.sql import SQLPanel
from debug_toolbar.utils import matched_route


class SQLAlchemyPanel(SQLPanel):
    title = "SQLAlchemy"

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
        query = {
            "duration": (perf_counter() - conn.info["start_time"].pop(-1)) * 1000,
            "sql": statement,
            "params": parameters,
            "is_select": context.invoked_statement.is_select,
        }
        self.add_query(str(conn.engine.url), query)

    async def process_request(self, request: Request) -> Response:
        engines: t.List[Engine] = []
        route = matched_route(request)

        if hasattr(route, "dependant"):
            route = t.cast(APIRoute, route)
            try:
                solved_result = await solve_dependencies(
                    request=request,
                    dependant=route.dependant,
                    dependency_overrides_provider=route.dependency_overrides_provider,
                )
            except Exception:
                pass
            else:
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
