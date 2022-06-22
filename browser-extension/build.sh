#!/usr/bin/env bash

#
# Build a .zip target that can be uploaded to:
# - Chrome Web Store
# - Firefox Add-ons
#

set -eu

SCRIPT_PATH="$(realpath -e "$(dirname "$0")")"
SOURCE_DIR='src'
TARGET_BASENAME='tournesol_extension.zip'


pushd ${SCRIPT_PATH} > /dev/null

# zip the sources
pushd ${SOURCE_DIR} > /dev/null
zip -r -FS ../${TARGET_BASENAME} *
popd > /dev/null

# zip the license
zip ${TARGET_BASENAME} LICENSE
popd > /dev/null

