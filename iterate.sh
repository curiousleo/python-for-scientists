#!/usr/bin/env bash

# Run tests and linter whenever demoodle.py changes
echo demoodle.py | entr -cs 'pytest -v demoodle.py && flake8 --config flake8.ini demoodle.py'
