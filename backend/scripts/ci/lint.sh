#!/usr/bin/env bash
set -uxo pipefail

# Python Code Quality Checks

# return 0 if all checks return 0
# 1 instead

pylint --rcfile=.pylintrc core tournesol
chk1=$?

flake8 --config=.flake8 core tournesol
chk2=$?

exit $chk1 && $chk2
