import typing as t
from contextlib import contextmanager
from time import perf_counter

from fastapi import Request, Response
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.transactions import current_transaction_map

from debug_toolbar.panels.sql import SQLPanel, raw_sql


class DBWrapper:
    def __init__(self, db: BaseDBAsyncClient, on_execute: t.Callable[..., t.Any]):
        self.db = db
        self.on_execute = on_execute

    def __getattr__(self, attr: str) -> t.Any:
        return getattr(self.db, attr)

    async def execute_insert(self, query: str, values: list) -> t.Any:
        with self.on_execute(self.db, query, values):
            return await self.db.execute_insert(query, values)

    async def execute_query(
        self,
        query: str,
        values: t.Optional[list] = None,
    ) -> t.Tuple[int, t.Sequence[dict]]:
        with self.on_execute(self.db, query, values):
            return await self.db.execute_query(query, values)

    async def execute_script(self, query: str) -> None:
        with self.on_execute(self.db, query):
            self.db.execute_script(query)

    async def execute_many(self, query: str, values: t.List[list]) -> None:
        with self.on_execute(self.db, query, values):
            await self.db.execute_many(query, values)

    async def execute_query_dict(
        self,
        query: str,
        values: t.Optional[list] = None,
    ) -> t.List[dict]:
        with self.on_execute(self.db, query, values):
            return await self.db.execute_query_dict(query, values)


class TortoisePanel(SQLPanel):
    title = "Tortoise ORM"

    @contextmanager
    def on_execute(
        self,
        db: BaseDBAsyncClient,
        statement: str,
        values: t.Any = None,
    ) -> t.Iterator[None]:
        start_time = perf_counter()
        try:
            yield
        finally:
            query = {
                "duration": (perf_counter() - start_time) * 1000,
                "sql": statement,
                "raw": raw_sql(statement),
                "params": values,
                "is_select": statement.lower().strip().startswith("select"),
            }
            self.add_query(db.connection_name, query)

    async def process_request(self, request: Request) -> Response:
        for db in current_transaction_map.values():
            db.set(DBWrapper(db.get(), self.on_execute))
        try:
            response = await super().process_request(request)
        finally:
            for db in current_transaction_map.values():
                db.set(db.get().db)
        return response
