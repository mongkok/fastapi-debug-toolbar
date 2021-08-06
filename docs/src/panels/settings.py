from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI
from pydantic import BaseSettings, SecretStr


class APISettings(BaseSettings):
    SECRET_KEY: SecretStr


app = FastAPI(debug=True)
app.add_middleware(DebugToolbarMiddleware, settings=[APISettings()])
