#!/usr/bin/env bash

set -Eeuo pipefail

export ANSIBLE_HOST="tournesol-prod"
export DOMAIN_NAME="tournesol.app"

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR/.."

if [[ "${1:-""}" == "apply" ]]
then
  CHECK="apply"
else
  CHECK=""
fi

./scripts/deploy-with-secrets.sh "$CHECK"
