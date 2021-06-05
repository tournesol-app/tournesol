#!/usr/bin/env bash

set -Eeuo pipefail

CURRENT_DIR="$(dirname "$0")"

cd "$CURRENT_DIR"

DB_NAME="emails-to-notify.sqlite"

QUERY="select * from emails;"

[[ -f "$DB_NAME" ]] && \
sqlite3 "$DB_NAME" <<< "$QUERY"
