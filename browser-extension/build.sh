#!/usr/bin/env bash

#
# Build a .zip target that can be uploaded to:
# - Chrome Web Store
# - Firefox Add-ons
#

set -eu

usage() { echo "Usage: $0 [-o tournesol_extension.zip]" 1>&2 ; }

SCRIPT_PATH="$(realpath -e "$(dirname "$0")")"
SOURCE_DIR='src'
OUTPUT_FILE='tournesol_extension.zip'

while getopts "ho:" opt; do
    case $opt in
        o ) OUTPUT_FILE=$OPTARG;;
        h ) usage
        exit 0;;
        *) usage
        exit 1;;
    esac
done

pushd "${SCRIPT_PATH}" > /dev/null

node prepareExtension.js

# zip the sources
pushd ${SOURCE_DIR} > /dev/null
zip -r -FS ../"${OUTPUT_FILE}" ./*
popd > /dev/null

# zip the license
zip "${OUTPUT_FILE}" LICENSE
popd > /dev/null
