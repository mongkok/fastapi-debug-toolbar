import typing as t
from time import perf_counter

from fastapi import Request, Response
from fastapi.concurrency import AsyncExitStack
from fastapi.dependencies.utils import solve_dependencies
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.orm import Session

from debug_toolbar.panels.sql import SQLPanel


class SQLAlchemyPanel(SQLPanel):
    title = "SQLAlchemy"

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.engines: t.Set[Engine] = set()

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

    async def add_engines(self, request: Request):
        route = request.scope["route"]

        if hasattr(route, "dependant"):
            if request.scope.get("fastapi_astack") is None:
                async with AsyncExitStack() as stack:
                    request.scope["fastapi_astack"] = stack

            solved_result = await solve_dependencies(
                request=request,
                dependant=route.dependant,
                dependency_overrides_provider=route.dependency_overrides_provider,
            )
            for value in solved_result[0].values():
                if isinstance(value, Session):
                    self.engines.add(value.get_bind())

    async def process_request(self, request: Request) -> Response:
        await self.add_engines(request)

        for engine in self.engines:
            self.register(engine)
        try:
            response = await super().process_request(request)
        finally:
            for engine in self.engines:
                self.unregister(engine)
        return response
