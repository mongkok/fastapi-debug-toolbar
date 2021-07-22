#!/usr/bin/env bash

set -e
set -x

mypy debug_toolbar tests
flake8 debug_toolbar tests
black debug_toolbar tests --check
isort debug_toolbar tests --check-only
