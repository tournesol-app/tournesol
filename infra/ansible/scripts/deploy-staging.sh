#!/usr/bin/env bash

set -Eeuo pipefail

export ANSIBLE_HOST="tournesol-staging"
export DOMAIN_NAME="staging.tournesol.app"

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR/.."

./scripts/deploy-with-secrets.sh "${1:-"notapply"}" "${2:-"notfast"}"
