from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI

app = FastAPI(debug=True)
app.add_middleware(DebugToolbarMiddleware, profiler_options={'interval': .0002})
