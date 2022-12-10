import typing as t

import pytest
from _pytest.mark import MarkDecorator


def override_settings(**settings: t.Any) -> MarkDecorator:
    return pytest.mark.parametrize("settings", [settings])


def override_panels(panels: t.List[str]) -> MarkDecorator:
    return override_settings(panels=panels)
