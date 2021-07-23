#!/usr/bin/env bash

export SOURCE_FILES="debug_toolbar tests"

set -e
set -x

flake8 $SOURCE_FILES
black --check $SOURCE_FILES
isort --check-only $SOURCE_FILES
mypy --install-type --non-interactive $SOURCE_FILES
