from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base = declarative_base()
