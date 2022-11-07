#!/usr/bin/env bash

set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

set -x

DUMP_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DUMP_FILE="./db/dump_$DUMP_DATE.sql.gz"

docker exec tournesol-dev-db bash -c "pg_dump -U tournesol -d tournesol --exclude-table-data 'django_admin_log' --exclude-table-data 'django_session' --exclude-table-data 'oauth2*' | gzip > /tmp/dump.sql.gz"

docker cp tournesol-dev-db:/tmp/dump.sql.gz "$DUMP_FILE"

echo "Created $DUMP_FILE"
