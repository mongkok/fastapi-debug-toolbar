from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI

app = FastAPI(debug=True)
# This line must come before any compression middleware is added, e.g app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(DebugToolbarMiddleware)

