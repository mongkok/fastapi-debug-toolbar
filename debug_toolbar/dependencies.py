from __future__ import annotations

import typing as t
from contextlib import AsyncExitStack

from fastapi import HTTPException, Request
from fastapi.dependencies.utils import solve_dependencies


async def get_dependencies(request: Request) -> dict[str, t.Any] | None:
    route = request["route"]

    if hasattr(route, "dependant"):
        try:
            solved_result = await solve_dependencies(
                request=request,
                dependant=route.dependant,
                dependency_overrides_provider=route.dependency_overrides_provider,
                async_exit_stack=AsyncExitStack(),
            )
        except HTTPException:
            pass
        else:
            return solved_result[0]
    return None
