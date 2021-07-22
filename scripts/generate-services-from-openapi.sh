#!/usr/bin/env bash
set -Eeuxo pipefail

CURRENT_DIR="$(dirname "$0")"
cd "$CURRENT_DIR"

source "../.env.development"

mkdir -p tmp
wget -O tmp/openapi.yaml "$REACT_APP_API_URL/schema/"
cd ..
yarn run openapi
rm -rf tmp
