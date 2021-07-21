# FastAPI Debug Toolbar

A debug toolbar for FastAPI based on the original django-debug-toolbar.

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
