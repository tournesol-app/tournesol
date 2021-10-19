#!/usr/bin/env bash

set -Eeuo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR/.."

echo "Forgetting secrets"
source "./scripts/forget-secrets.sh"
echo "Fetching secrets"
source "./scripts/get-vm-secrets.sh" "$DOMAIN_NAME"

echo "Deploying"
./scripts/deploy-without-secrets.sh "${1:-"notapply"}" "${2:-"notfast"}"
