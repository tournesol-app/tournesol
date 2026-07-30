#!/usr/bin/env bash

#
# Build an Xcode project containing the Tournesol Safari Web Extension.
#

set -eu

usage() {
    echo "Usage: $0 [-o output-directory] [-b bundle-identifier-prefix]" 1>&2
}

SCRIPT_PATH="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
OUTPUT_DIRECTORY="${SCRIPT_PATH}/safari"
BUNDLE_IDENTIFIER_PREFIX='app.tournesol'

while getopts "ho:b:" opt; do
    case $opt in
        o ) OUTPUT_DIRECTORY=$OPTARG;;
        b ) BUNDLE_IDENTIFIER_PREFIX=$OPTARG;;
        h )
            usage
            exit 0
            ;;
        * )
            usage
            exit 1
            ;;
    esac
done

if ! xcrun --find safari-web-extension-packager > /dev/null 2>&1; then
    echo "The Safari Web Extension packager was not found. Install Xcode first." 1>&2
    exit 1
fi

pushd "${SCRIPT_PATH}" > /dev/null

EXTENSION_BROWSER=safari MANIFEST_VERSION=2 node prepareExtension.js

xcrun safari-web-extension-packager src \
    --project-location "${OUTPUT_DIRECTORY}" \
    --app-name Tournesol \
    --bundle-identifier "${BUNDLE_IDENTIFIER_PREFIX}.Tournesol" \
    --swift \
    --macos-only \
    --copy-resources \
    --no-open \
    --no-prompt \
    --force

popd > /dev/null
