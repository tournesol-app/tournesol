#!/usr/bin/env bash
set -Eeuxo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"
FRONTEND_ROOT=$(dirname $CURRENT_DIR)

cd "$CURRENT_DIR"

if [[ "${NODE_ENV:-"development"}" == "production" ]]; then
    source "../.env"
else
    source "../.env.development"
fi

cd ..
yarn run openapi

# Fix the syntax error generated by OpenAPI Typescript Codegen.
# See: https://github.com/ferdikoomen/openapi-typescript-codegen/issues/1299
if [ -f ${FRONTEND_ROOT}/src/services/openapi/models/BlankEnum.ts ]; then
    cp ${FRONTEND_ROOT}/scripts/patches/BlankEnum.ts ${FRONTEND_ROOT}/src/services/openapi/models/
fi
