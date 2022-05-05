#!/usr/bin/env bash

set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

set -x

curl -o ../frontend/scripts/openapi.yaml http://localhost:8000/schema/
docker exec tournesol-dev-front scripts/generate-services-from-openapi.sh
