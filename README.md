# FastAPI Debug Toolbar

<p align="center">
    <img src="https://user-images.githubusercontent.com/5514990/126553842-eb44400c-79e3-4037-9485-c16a1749b891.gif" alt="FastAPI Debug Toolbar">
</p>

<p align="center">
    <em>A debug toolbar for FastAPI based on the original django-debug-toolbar.</em>
</p>
<p align="center">
<a href="https://github.com/mongkok/fastapi-debug-toolbar/actions/workflows/build" target="_blank">
    <img src="https://github.com/mongkok/fastapi-debug-toolbar/actions/workflows/build/badge.svg" alt="Test">
</a>
<a href="https://codecov.io/gh/mongkok/fastapi-debug-toolbar" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/mongkok/fastapi-debug-toolbar" alt="Coverage">
</a>
<a href="https://pypi.org/project/fastapi-debug-toolbar" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-debug-toolbar" alt="Package version">
</a>

## Installation

```shell
pip install fastapi-debug-toolbar
```

## Quickstart

```py
from fastapi import FastAPI
from debug_toolbar.middleware import DebugToolbarMiddleware

app = FastAPI(debug=True)
app.add_middleware(DebugToolbarMiddleware)
```
