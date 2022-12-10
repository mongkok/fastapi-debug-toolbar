import typing as t

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ...testclient import TestClient
from .crud import create_user, get_user
from .database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)


def get_db() -> t.Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(app: FastAPI, get_index: t.Callable) -> TestClient:
    @app.get("/sql", response_class=HTMLResponse)
    async def get_sql(request: Request, db: Session = Depends(get_db)) -> str:
        user = create_user(db=db, username="test")
        get_user(db=db, user_id=user.id)
        get_user(db=db, user_id=user.id)
        return get_index(request)

    return TestClient(app)
