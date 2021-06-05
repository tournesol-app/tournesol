#!/usr/bin/env bash

set -Eeuo pipefail

CURRENT_DIR="$(dirname "$0")"

cd "$CURRENT_DIR"

DB_NAME="emails-to-notify.sqlite"

QUERY="create table emails (id integer primary key, email text not null unique, ip text not null, date integer not null);"

[[ -f "$DB_NAME" ]] && echo "database already exists" || \
sqlite3 "$DB_NAME" <<< "$QUERY"
