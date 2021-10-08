#!/usr/bin/env bash

set -Eeuo pipefail

export ANSIBLE_HOST="tournesol-vm"
export DOMAIN_NAME="tournesol-vm"

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR/.."

if [[ "${1:-""}" == "apply" ]]
then
  CHECK="apply"
else
  CHECK=""
fi

./scripts/deploy-with-secrets.sh "$CHECK"
