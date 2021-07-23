#!/usr/bin/env bash

set -e
set -x

mypy debug_toolbar tests --install-type --non-interactive
flake8 debug_toolbar tests --max-line-length 88
black debug_toolbar tests --check
isort debug_toolbar tests --check-only
