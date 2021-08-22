import sys
import typing as t

import pytest
from _pytest.mark import MarkDecorator


def override_settings(**settings: t.Any) -> MarkDecorator:
    return pytest.mark.parametrize("settings", [settings])


def override_panels(panels: t.List[str]) -> MarkDecorator:
    return override_settings(panels=panels)


skip_py37: MarkDecorator = pytest.mark.skipif(sys.version_info < (3, 8), reason="?")
skip_py36: MarkDecorator = pytest.mark.skipif(sys.version_info < (3, 7), reason="?")
