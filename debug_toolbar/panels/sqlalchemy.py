import typing as t
from importlib import import_module
from time import perf_counter

from fastapi import Request, Response
from fastapi.dependencies.utils import (
    solve_dependencies,
    is_gen_callable,
)
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
        url = conn.engine.url
        name = f"{url.drivername}://****@****:{url.port}/{url.database}"
        self.add_query(name, query)

    async def process_request(self, request: Request) -> Response:
        engines: t.Set[Engine] = set()
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
                        engines.add(engine)
                        self.register(engine)
        for generator_path in self.toolbar.settings.SESSION_GENERATORS:
            generator_module = import_module(generator_path.split(":")[0])
            generator = getattr(generator_module, generator_path.split(":")[1])
            if is_gen_callable(generator):
                try:
                    value = next(generator())
                except TypeError:
                    value = next(generator(request))
                engine = value.get_bind()
                engines.add(engine)
                self.register(engine)
            else:
                try:
                    async for v in generator():
                        engine = v.get_bind()
                        engines.add(engine)
                        self.register(engine)
                except TypeError:
                    async for v in generator(request):
                        engine = v.get_bind()
                        engines.add(engine)
                        self.register(engine)
        try:
            response = await super().process_request(request)
        finally:
            for engine in engines:
                self.unregister(engine)
        return response
