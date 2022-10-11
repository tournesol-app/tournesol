#!/usr/bin/env bash

set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

set -x

DUMP_DATE=$(date +%Y-%m-%d)

docker exec tournesol-dev-db bash -c "pg_dump -U tournesol -d tournesol --exclude-table-data 'django_admin_log' --exclude-table-data 'django_session' --exclude-table-data 'oauth2*' > /tmp/dump.sql && tar cvzf /tmp/dump.sql.tgz -C /tmp dump.sql && rm /tmp/dump.sql"
docker cp tournesol-dev-db:/tmp/dump.sql.tgz "dump_$DUMP_DATE.sql.tgz"
