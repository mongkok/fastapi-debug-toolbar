import typing as t

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, sessionmaker

from ...testclient import TestClient
from .crud import create_user, get_user
from .database import Base, engine

Base.metadata.create_all(bind=engine)


@pytest.fixture
def get_db(session_options: dict[str, t.Any]) -> t.Callable:
    SessionLocal = sessionmaker(**session_options or {"bind": engine})

    def f() -> t.Generator:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return f


@pytest.fixture
def client(app: FastAPI, get_index: t.Callable, get_db: t.Callable) -> TestClient:
    @app.get("/sql", response_class=HTMLResponse)
    async def get_sql(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
        user = create_user(db=db, username=str(id(get_db)))
        get_user(db=db, user_id=user.id)
        get_user(db=db, user_id=user.id)
        return get_index(request)

    return TestClient(app)
