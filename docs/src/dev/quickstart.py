from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

app = FastAPI(debug=True)
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    DebugToolbarMiddleware,
    panels=["panels.ExamplePanel"],
    jinja_loaders=[templates.env.loader],
)
