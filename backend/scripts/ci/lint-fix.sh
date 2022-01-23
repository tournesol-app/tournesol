#!/usr/bin/env bash
set -euxo pipefail

# Python Code Quality Fixes

isort --settings-path .isort.cfg ${@:-core ml settings tournesol}
