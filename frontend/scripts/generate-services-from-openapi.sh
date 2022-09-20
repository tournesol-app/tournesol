#!/usr/bin/env bash
set -Eeuxo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"
cd "$CURRENT_DIR"

if [[ "${NODE_ENV:-"development"}" == "production" ]]; then
    source "../.env"
else
    source "../.env.development"
fi

# mkdir -p tmp
# wget -O tmp/openapi.yaml "$REACT_APP_API_URL/schema/"
cd ..
yarn run openapi
# rm -rf tmp
