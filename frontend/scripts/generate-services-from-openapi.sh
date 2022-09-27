#!/usr/bin/env bash
set -Eeuxo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"
cd "$CURRENT_DIR"

if [[ "${NODE_ENV:-"development"}" == "production" ]]; then
    source "../.env"
else
    source "../.env.development"
fi

cd ..
yarn run openapi
