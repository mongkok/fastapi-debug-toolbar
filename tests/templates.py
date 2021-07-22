import typing as t

from fastapi.templating import Jinja2Templates as BaseJinja2Templates


class Jinja2Templates(BaseJinja2Templates):
    # See: encode/starlette/issues/472

    def TemplateResponse(self, template: str, context: t.Any) -> str:  # type: ignore
        return self.get_template(template).render(**context)
