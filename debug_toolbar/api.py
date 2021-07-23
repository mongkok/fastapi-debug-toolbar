import html
import typing as t

from fastapi import Request

from debug_toolbar.toolbar import DebugToolbar


def render_panel(request: Request, store_id: str, panel_id: str) -> t.Any:
    toolbar = DebugToolbar.fetch(store_id)

    if toolbar is None:
        content = (
            "Data for this panel isn't available anymore. "
            "Please reload the page and retry."
        )
        content = f"<p>{html.escape(content)}</p>"
        scripts = []
    else:
        panel = toolbar.get_panel_by_id(panel_id)
        content = panel.content
        scripts = panel.scripts

    return {"content": content, "scripts": scripts}
