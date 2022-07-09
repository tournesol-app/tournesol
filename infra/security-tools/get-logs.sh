#!/usr/bin/env bash

set -Eeuxo pipefail

CURRENT_DIR="$(dirname "$(realpath "$0")")"

cd "$CURRENT_DIR"

LOGS_FILES="\
/var/log/auth.log*
/var/log/nginx/json_access.log*
/var/log/postgresql/postgresql-13-main.log*
"

SSH_USERNAME="${1:-USER}"
SERVER_ADDRESS="tournesol.app"

rm logs/* || true
mkdir -p logs
REMOTE_TMP_DIR="$(ssh "$SSH_USERNAME@$SERVER_ADDRESS" -- mktemp -d)"

for lf in $LOGS_FILES
do
    basename "$lf"
    ssh "$SSH_USERNAME@$SERVER_ADDRESS" -- \
        sudo cp "$lf" "$REMOTE_TMP_DIR/"
    ssh "$SSH_USERNAME@$SERVER_ADDRESS" -- \
        sudo chown "$SSH_USERNAME:$SSH_USERNAME" "$REMOTE_TMP_DIR/$(basename "$lf")"
    scp "$SSH_USERNAME@$SERVER_ADDRESS:$REMOTE_TMP_DIR/$(basename "$lf")" logs/
done

LOGS_BASE_NAMES="\
auth.log
json_access.log
postgresql-13-main.log
"

for lbn in $LOGS_BASE_NAMES
do
    gunzip logs/$lbn.*.gz
    cat logs/$lbn.* > "logs/${lbn%.log}-all.log"
    rm logs/$lbn{,.*}
done

ssh "$SSH_USERNAME@$SERVER_ADDRESS" -- \
    rm -r "$REMOTE_TMP_DIR"

ssh "$SSH_USERNAME@$SERVER_ADDRESS" -- \
    sudo journalctl -o json -u ssh > logs/ssh.log.json
ssh "$SSH_USERNAME@$SERVER_ADDRESS" -- \
    sudo journalctl -o json -u gunicorn > logs/gunicorn.log.json
