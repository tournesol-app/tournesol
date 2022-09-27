#!/usr/bin/env bash
set -euxo pipefail

# Python Code Quality Fixes

isort --settings-path .isort.cfg ${@:-core faq ml settings tournesol twitterbot vouch}
