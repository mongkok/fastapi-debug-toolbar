import typing as t

import pytest
from _pytest.mark import MarkDecorator
from fastapi import FastAPI

from debug_toolbar.middleware import DebugToolbarMiddleware


def override_settings(**settings: t.Any) -> MarkDecorator:
    app = FastAPI(debug=True)
    app.add_middleware(DebugToolbarMiddleware, **settings)
    return pytest.mark.parametrize("app", [app])
