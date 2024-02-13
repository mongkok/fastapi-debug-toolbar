from debug_toolbar.panels.sqlalchemy import SQLAlchemyPanel as BasePanel
from sqlalchemy import create_engine

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})


class SQLAlchemyPanel(BasePanel):
    async def add_engines(self, request: Request):
        self.engines.add(engine)
