from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy.orm import Session

from . import models


def create_user(db: Session, username: str) -> models.User:
    user = models.User(username=username)
    db.add(user)
    db.commit()
    return user


def get_user(db: Session, user_id: Column[int]) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()
