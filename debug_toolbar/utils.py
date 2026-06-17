from __future__ import annotations

import asyncio
import functools
import inspect
import sys
import typing as t

from fastapi import Request
from fastapi.routing import APIRoute
from pydantic_extra_types.color import Color
from starlette.routing import BaseRoute, Match


@functools.lru_cache(maxsize=1)
def _included_router_cls() -> type | None:
    # FastAPI >= 0.137 uses lazy router inclusion and exposes the internal
    # node type here. Absent on older versions.
    try:
        from fastapi.routing import _IncludedRouter

        return _IncludedRouter
    except ImportError:
        return None


def iter_effective_routes(
    routes: t.Iterable[BaseRoute],
) -> t.Iterator[BaseRoute]:
    """Yield concrete, matchable/displayable routes.

    FastAPI >= 0.137 introduced lazy router inclusion: ``include_router``
    appends an internal ``_IncludedRouter`` node (a ``BaseRoute`` with no
    ``.path``) to ``app.routes`` instead of eagerly flattening the included
    routes. Expand those nodes into their effective, correctly-prefixed route
    contexts (each exposing ``.path``/``.name``/``.methods``/``.endpoint`` and
    a working ``.matches``) so callers can treat every entry uniformly. A
    no-op on FastAPI versions without ``_IncludedRouter``.
    """
    included = _included_router_cls()
    for route in routes:
        if included is not None and isinstance(route, included):
            yield from route.effective_route_contexts()
        else:
            yield route


def import_string(import_name: str) -> t.Any:
    try:
        __import__(import_name)
    except ImportError:
        if "." not in import_name:
            raise
    else:
        return sys.modules[import_name]

    module_name, obj_name = import_name.rsplit(".", 1)
    module = __import__(module_name, globals(), locals(), [obj_name])
    try:
        return getattr(module, obj_name)
    except AttributeError as e:
        raise ImportError(e) from None


def get_name_from_obj(obj: t.Any) -> str:
    if hasattr(obj, "__name__"):
        name = obj.__name__
    else:
        name = obj.__class__.__name__

    if hasattr(obj, "__module__"):
        name = f"{obj.__module__}.{name}"
    return name


def matched_route(request: Request) -> APIRoute | None:
    for route in iter_effective_routes(request.app.routes):
        match, _ = route.matches(request.scope)

        if match == Match.FULL:
            if hasattr(route, "endpoint"):
                # For expanded _IncludedRouter contexts, hand back the real
                # underlying route object (FastAPI stores the same in
                # ``scope["route"]``); plain routes are returned as-is.
                return getattr(route, "original_route", route)
            break
    return None


def is_coroutine(endpoint: t.Callable) -> bool:
    handler = endpoint

    while isinstance(handler, functools.partial):
        handler = handler.func
    if not (inspect.ismethod(handler) or inspect.isfunction(handler)):
        handler = handler.__call__  # type: ignore[operator]
    return asyncio.iscoroutinefunction(handler)


def pluralize(value: int, arg: str = "s") -> str:
    if "," not in arg:
        arg = f",{arg}"

    bits = arg.split(",")

    if len(bits) > 2:
        return ""

    singular_suffix, plural_suffix = bits[:2]

    if value == 1:
        return singular_suffix
    return plural_suffix


def color_generator() -> t.Generator[Color, None, None]:
    triples = [
        (0, 1, 1),
        (1, 1, 0),
        (1, 0, 1),
        (1, 1, 1),
        (0, 1, 0),
        (0, 0, 1),
    ]
    n = 1 << 7
    so_far = [[0, 0, 0]]
    while True:
        if n == 0:
            yield Color("black")
        copy_so_far = list(so_far)
        for triple in triples:
            for previous in copy_so_far:
                rgb = [n * triple[i] + previous[i] for i in range(3)]
                so_far.append(rgb)
                yield Color(f"rgb{tuple(rgb)}")
        n >>= 1
