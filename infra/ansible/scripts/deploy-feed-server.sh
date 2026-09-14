#!/usr/bin/env bash

set -Eeuo pipefail

ANSIBLE_HOST="${1:?usage: deploy-feed-server.sh <ansible-host> [apply]}"

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR/.."

if [[ "${2:-""}" == "apply" ]]
then
  CHECK=""
else
  CHECK="--check"
fi

GIT_REFERENCE="${GIT_REFERENCE:-$(git rev-parse HEAD)}"

ansible-playbook -i inventory.yml -l "$ANSIBLE_HOST" feed-server.yml \
  $CHECK \
  -e "git_reference=${GIT_REFERENCE}"
