#!/usr/bin/env bash

set -Eeuxo pipefail

CURRENT_DIR="$(dirname "$0")"

cd "$CURRENT_DIR"

for f in "ubuntu-20.04.2-live-server-amd64.iso" "SHA256SUMS" "SHA256SUMS.gpg"
do
    [[ -f "$f" ]] || wget "https://releases.ubuntu.com/20.04.2/$f"
done

# If key verification fails because you miss the signing public key, get it from the verification output and set it here to retrieve it
RSA_KEY_FINGERPRINT="0x843938DF228D22F7B3742BC0D94AA3F0EFE21092"
gpg --list-keys "$RSA_KEY_FINGERPRINT" || \
gpg --keyid-format long --keyserver hkp://keyserver.ubuntu.com --recv-keys "$RSA_KEY_FINGERPRINT"

gpg --keyid-format long --verify "SHA256SUMS.gpg" "SHA256SUMS"

sha256sum -c "SHA256SUMS" 2>&1 | grep OK


