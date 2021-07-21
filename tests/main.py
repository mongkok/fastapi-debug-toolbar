from fastapi import FastAPI

from debug_toolbar.middleware import DebugToolbarMiddleware

app = FastAPI(debug=True)
app.add_middleware(DebugToolbarMiddleware)
