#!/usr/bin/env bash
set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

ssh "$VM_USER@$VM_ADDR" -- sudo -u postgres pg_dump -d tournesol -t tournesol_video -t tournesol_comparison -t core_user -a --inserts > dump.sql
tar cvzf dump.sql.tgz dump.sql
rm dump.sql
