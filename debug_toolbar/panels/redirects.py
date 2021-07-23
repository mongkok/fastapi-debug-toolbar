import typing as t

from fastapi import Request, Response, status

from debug_toolbar.panels import Panel
from debug_toolbar.responses import StreamingHTMLResponse


class RedirectsPanel(Panel):
    has_content = False
    nav_title = "Intercept redirects"
    template = "redirect.html"

    async def process_request(self, request: Request) -> Response:
        response = await super().process_request(request)

        if 300 <= response.status_code < 400:
            redirect_to = response.headers.get("Location")

            if redirect_to:

                async def content() -> t.AsyncGenerator[str, None]:
                    yield self.render(
                        redirect_to=redirect_to,
                        status_code=response.status_code,
                    )

                response = StreamingHTMLResponse(
                    content=content(),
                    status_code=status.HTTP_200_OK,
                )
        return response
