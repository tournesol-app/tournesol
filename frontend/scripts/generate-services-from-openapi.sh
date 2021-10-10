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

# workaround for bug in quote handling
sed -i 's/Côte d'\''Ivoire/Côte d\\'\''Ivoire/' src/services/openapi/models/NationalityEnum.ts
sed -i 's/Côte d'\''Ivoire/Côte d\\'\''Ivoire/' src/services/openapi/models/ResidenceEnum.ts
