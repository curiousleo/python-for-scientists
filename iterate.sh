#!/usr/bin/env bash

# Run tests and linter whenever demoodle.py changes
ls *.py | entr -cs 'poetry run pytest -v *.py && flake8 --config flake8.ini *.py'
