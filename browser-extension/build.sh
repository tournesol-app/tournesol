#!/usr/bin/env bash

#
# Build a .zip target that can be uploaded to:
# - Chrome Web Store
# - Firefox Add-ons
#

set -eu

TARGET='tournesol_extension.zip'

pushd src
zip -r -FS ../${TARGET} *
popd

zip ${TARGET} LICENSE

