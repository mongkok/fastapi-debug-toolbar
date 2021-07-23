import sys

import pytest
from _pytest.mark import MarkDecorator


skip_py37: MarkDecorator = pytest.mark.skipif(sys.version_info < (3, 8), reason="?")
