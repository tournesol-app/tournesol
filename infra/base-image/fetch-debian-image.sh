#!/usr/bin/env bash

set -Eeuxo pipefail

DEBIAN_VERSION="11.6.0"
CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR"

for f in "debian-${DEBIAN_VERSION}-amd64-netinst.iso" "SHA256SUMS" "SHA256SUMS.sign"
do
    [[ -f "$f" ]] || wget "http://debian.ethz.ch/debian-cd/${DEBIAN_VERSION}/amd64/iso-cd/$f"
done

# If key verification fails because you miss the signing public key, get it from the verification output and set it here to retrieve it
RSA_KEY_FINGERPRINT="0xDF9B9C49EAA9298432589D76DA87E80D6294BE9B"
gpg --list-keys "$RSA_KEY_FINGERPRINT" || \
gpg --keyid-format long --recv-keys "$RSA_KEY_FINGERPRINT"

gpg --keyid-format long --verify "SHA256SUMS.sign" "SHA256SUMS"

sha256sum -c "SHA256SUMS" 2>&1 | grep OK
