import typing as t

from tortoise.queryset import QuerySetSingle

from . import models


def create_user(username: str) -> t.Coroutine[t.Any, t.Any, models.User]:
    return models.User.create(username=username)


def get_user(user_id: int) -> QuerySetSingle[models.User]:
    return models.User.get(id=user_id)
