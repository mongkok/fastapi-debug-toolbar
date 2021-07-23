import typing as t

from fastapi import Request, Response

from debug_toolbar.panels import Panel


class HeadersPanel(Panel):
    title = "Headers"
    template = "panels/headers.html"

    async def generate_stats(
        self,
        request: Request,
        response: Response,
    ) -> t.Optional[t.Dict[str, t.Any]]:
        request_headers = dict(request.headers)

        if "cookie" in request_headers:
            request_headers["cookie"] = "=> see Request panel"

        return {
            "request_headers": request_headers,
            "environ": request.scope.get("asgi", {}),
            "response_headers": response.headers,
        }
