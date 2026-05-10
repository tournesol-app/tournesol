#!/usr/bin/env bash
# Upgrades the PostgreSQL 13 'main' cluster to 17.
# PG13 is left intact as a fallback (stopped, data preserved).
#
# Usage:
#   sudo ./pg-upgrade-13-to-17.sh
#
# Upgrade procedure:
#   1. Run ansible, with maintenance mode enabled, to install PG17
#   2. Run `sudo ./pg-upgrade-13-to-17.sh` to migrate the db to PG17
#   3. Rerun ansible, with maintenance mode off.
#   4. Drop old cluster with `pg_dropcluster 13 main`

set -euo pipefail

OLD_VER=13
NEW_VER=17
CLUSTER=main

# Drop obsolete views in schema prometheus.
sudo -u postgres psql -d postgres -c 'DROP VIEW IF EXISTS prometheus.pg_stat_activity'
sudo -u postgres psql -d postgres -c 'DROP VIEW IF EXISTS prometheus.pg_stat_replication'

sudo -u postgres pg_upgradecluster --method upgrade -v "$NEW_VER" "$OLD_VER" "$CLUSTER"

# Make sure systemd can see the new cluster as started
sudo pg_ctlcluster $NEW_VER $CLUSTER stop
sudo systemctl start postgresql@$NEW_VER-$CLUSTER.service
