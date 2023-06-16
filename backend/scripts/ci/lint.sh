#!/usr/bin/env bash
set -uxo pipefail

# Python Code Quality Checks

# return 0 if all checks return 0
# 1 instead

isort --settings-path .isort.cfg --check-only ${@:-core faq ml settings tournesol twitterbot vouch backoffice}
chk1=$?

flake8 --config=.flake8 ${@:-}
chk2=$?

pylint --rcfile=.pylintrc ${@:-core faq ml tournesol twitterbot vouch backoffice}
chk3=$?

! (( chk1 || chk2 || chk3 ))
