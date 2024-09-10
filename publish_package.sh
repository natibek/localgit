#!/bin/bash

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
toplevel=$(git rev-parse --show-toplevel --path-format=absolute)

# This publishes checks-superstaq to PyPI.
cd "$toplevel"
python -m build
twine upload dist/* -u __token__ -p "$PYPI_API_KEY"
