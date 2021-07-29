# FastAPI Debug Toolbar

<p align="center">
    <img src="https://user-images.githubusercontent.com/5514990/127530804-7c076554-6cf2-4a7f-923f-e40b7f949441.gif" alt="FastAPI Debug Toolbar">
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

## Installation

```sh
pip install fastapi-debug-toolbar
```

## Quickstart

```py
from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI

app = FastAPI(debug=True)
app.add_middleware(DebugToolbarMiddleware)
```
