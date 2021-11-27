#!/usr/bin/env bash

set -Eeuo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"
cd "$CURRENT_DIR"

./fetch-and-import-pg-backup.sh --backup-name "$(./list-backups.sh tournesol.app | head -n1)" --from tournesol.app --to-ansible-host tournesol-staging
