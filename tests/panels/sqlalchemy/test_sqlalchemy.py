from __future__ import annotations

import typing as t

import pytest
from sqlalchemy.orm import declarative_base

from ...mark import override_panels
from ...testclient import TestClient
from .database import Base, engine


@override_panels(["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"])
@pytest.mark.parametrize(
    "session_options",
    (None, {"binds": {Base: engine, declarative_base(): engine}}),
)
def test_sqlalchemy(client: TestClient, session_options: dict[str, t.Any]) -> None:
    store_id = client.get_store_id("/sql")
    stats = client.get_stats(store_id, "SQLAlchemyPanel")
    queries = stats["queries"]

    assert len(queries) == 4
    assert queries[0][1]["sql"].startswith("INSERT")
    assert queries[2][1]["dup_count"] == 2
