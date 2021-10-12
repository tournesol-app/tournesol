#!/usr/bin/env bash

set -Eeuo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR/.."

source "./scripts/forget-secrets.sh"
source "./scripts/get-vm-secrets.sh" "$DOMAIN_NAME"

if [[ "${1:-""}" == "apply" ]]
then
  CHECK="apply"
else
  CHECK=""
fi

./scripts/deploy-without-secrets.sh "$CHECK"
