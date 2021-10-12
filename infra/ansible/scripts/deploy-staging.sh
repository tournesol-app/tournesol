#!/usr/bin/env bash

set -Eeuo pipefail

export ANSIBLE_HOST="tournesol-staging"
export DOMAIN_NAME="staging.tournesol.app"

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR/.."

if [[ "${1:-""}" == "apply" ]]
then
  CHECK="apply"
else
  CHECK=""
fi

./scripts/deploy-with-secrets.sh "$CHECK"
