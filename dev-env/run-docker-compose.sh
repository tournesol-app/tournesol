#!/usr/bin/env bash

set -Eeuxo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"
cd "$CURRENT_DIR"

sudo rm -rf code data

mkdir code
cp -r ../core ../settings ../templates ../tournesol ../ml ../manage.py ../requirements.txt code/

docker-compose up --build --force-recreate -d

echo 'Waiting a Bit for Backend to be Ready...'
sleep 30

echo 'Importing public dataset'
tar xvf "$CURRENT_DIR"/../scripts/dataset-import/dump-for-migrations-core-0004-tournesol-0007.sql.tgz
sudo mv dump.sql "$CURRENT_DIR"/data/db/
sudo chown 999:999 "$CURRENT_DIR"/data/db/dump.sql
docker exec --env PGPASSWORD=password dev-env_db_1 bash -c "psql -1 -q -d tournesol -U user < /var/lib/postgresql/data/dump.sql"
sudo rm "$CURRENT_DIR"/data/db/dump.sql

echo 'Creating Superuser:'
# docker exec -ti dev-env_web_1 python manage.py createsuperuser
USERNAME="${1:-"$USER"}"
PASSWORD="${2:-"yop"}"
EMAIL="${3:-"$USER@kleis.ch"}"
./create-superuser.exp "$USERNAME" "$PASSWORD" "$EMAIL"

echo 'Creating OAuth Application:'
# OAUTH_CLIENT_ID="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)" || true
# OAUTH_CLIENT_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)" || true
OAUTH_CLIENT_ID="YlfkLzvVjmGw3gjJzdlFuMFWcR64fAk4WNg5ucGg"
OAUTH_CLIENT_SECRET="iB9j9hM5ekFpKlZQ6uNGloFJIWLVnq8LoG7SNdCtHY5oM7w9KY0XjpaDuwwJ40BshH7jKYZmXniaybhrQf5p4irAOMWv82RdYRMD6TTSJciZEAxn9onpKQoUgUeDqsRj"
now="$(date +%Y-%m-%d)"
docker exec --env PGPASSWORD=password dev-env_db_1 bash -c "psql -d tournesol -U user <<< \"insert into oauth2_provider_application (client_id, redirect_uris, client_type, authorization_grant_type, client_secret, name, skip_authorization, algorithm, created, updated) values ('$OAUTH_CLIENT_ID', 'http://localhost:8000/admin/', 'confidential', 'password', '$OAUTH_CLIENT_SECRET','Frontend', true, 'RS256', '$now', '$now');\""
