# ![FastAPI](https://raw.githubusercontent.com/mongkok/fastapi-debug-toolbar/main/debug_toolbar/statics/img/icon-green.svg) Debug Toolbar

<p align="center">
    <a href="https://fastapi-debug-toolbar.domake.io">
        <img src="https://user-images.githubusercontent.com/5514990/131232994-621774a8-1662-468d-87d8-2199b93387d6.gif" alt="FastAPI Debug Toolbar">
    </a>
</p>
<p align="center">
    <em>🐞A debug toolbar for FastAPI based on the original django-debug-toolbar.🐞</em>
    <br><em><b>Swagger UI</b> & <b>GraphQL</b> are supported.</em>
</p>
<p align="center">
    <a href="https://github.com/mongkok/fastapi-debug-toolbar/actions">
        <img src="https://github.com/mongkok/fastapi-debug-toolbar/actions/workflows/test-suite.yml/badge.svg" alt="Test">
    </a>
    <a href="https://codecov.io/gh/mongkok/fastapi-debug-toolbar">
        <img src="https://img.shields.io/codecov/c/github/mongkok/fastapi-debug-toolbar?color=%2334D058" alt="Coverage">
    </a>
    <a href="https://www.codacy.com/gh/mongkok/fastapi-debug-toolbar/dashboard">
        <img src="https://app.codacy.com/project/badge/Grade/e9d8ba3973264424a3296016063b4ab5" alt="Codacy">
    </a>
    <a href="https://pypi.org/project/fastapi-debug-toolbar">
        <img src="https://img.shields.io/pypi/v/fastapi-debug-toolbar" alt="Package version">
    </a>
</p>


---

**Documentation**: [https://fastapi-debug-toolbar.domake.io](https://fastapi-debug-toolbar.domake.io)

---

## Installation

```sh
pip install fastapi-debug-toolbar
```

## Quickstart

Add `DebugToolbarMiddleware` middleware to your FastAPI application:

```py
from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI

app = FastAPI(debug=True)
app.add_middleware(DebugToolbarMiddleware)
```

## SQLAlchemy

Please make sure to use the *"Dependency Injection"* system as described in the [FastAPI docs](https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency) and add the `SQLAlchemyPanel` to your panel list:

```py
app.add_middleware(
    DebugToolbarMiddleware,
    panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
)
```

## Tortoise ORM

Add the `TortoisePanel` to your panel list:

```py
app.add_middleware(
    DebugToolbarMiddleware,
    panels=["debug_toolbar.panels.tortoise.TortoisePanel"],
)
```
