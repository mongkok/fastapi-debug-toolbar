import typing as t
from time import perf_counter

from fastapi import Request, Response
from fastapi.concurrency import AsyncExitStack
from fastapi.dependencies.utils import solve_dependencies
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine, ExecutionContext
from sqlalchemy.orm import Session

from debug_toolbar.panels.sql import SQLPanel


class SQLAlchemyPanel(SQLPanel):
    title = "SQLAlchemy"

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.engines: t.Set[Engine] = set()

    def register(self, engine: Engine) -> None:
        event.listen(engine, "before_cursor_execute", self.before_execute, named=True)
        event.listen(engine, "after_cursor_execute", self.after_execute, named=True)

    def unregister(self, engine: Engine) -> None:
        event.remove(engine, "before_cursor_execute", self.before_execute)
        event.remove(engine, "after_cursor_execute", self.after_execute)

    def before_execute(self, context: ExecutionContext, **kwargs: t.Any) -> None:
        context._start_time = perf_counter()  # type: ignore[attr-defined]

    def after_execute(self, context: ExecutionContext, **kwargs: t.Any) -> None:
        query = {
            "duration": (
                perf_counter() - context._start_time  # type: ignore[attr-defined]
            )
            * 1000,
            "sql": context.statement,
            "params": context.parameters,
        }
        self.add_query(str(context.engine.url), query)

    async def add_engines(self, request: Request):
        route = request["route"]

        if hasattr(route, "dependant"):
            if "fastapi_astack" not in request:
                async with AsyncExitStack() as stack:
                    request.scope["fastapi_astack"] = stack

            solved_result = await solve_dependencies(
                request=request,
                dependant=route.dependant,
                dependency_overrides_provider=route.dependency_overrides_provider,
            )
            for value in solved_result[0].values():
                if isinstance(value, Session):
                    bind = value.get_bind()

                    if isinstance(bind, Connection):
                        self.engines.add(bind.engine)
                    else:
                        self.engines.add(bind)

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
