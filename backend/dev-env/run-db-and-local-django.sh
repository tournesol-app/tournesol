#!/usr/bin/env bash

set -Eeuxo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"
cd "$CURRENT_DIR"

sudo rm -rf data static media

mkdir data
sudo chown -R 999:999 data

docker-compose up --force-recreate -d db

sleep 30

cd ..

python3.9 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt

sed \
-e 's/DATABASE_HOST: db/DATABASE_HOST: 127.0.0.1/' \
-e 's|STATIC_ROOT: /tournesol/static|STATIC_ROOT: '"$CURRENT_DIR/static/"'|' \
-e 's|MEDIA_ROOT: /tournesol/media/|MEDIA_ROOT: '"$CURRENT_DIR/media/"'|' \
"$CURRENT_DIR/settings-tournesol.yaml" > "$CURRENT_DIR/settings-tournesol-local.yaml"
export SETTINGS_FILE="$CURRENT_DIR/settings-tournesol-local.yaml"

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

echo 'Importing public dataset'
tar xvf "$CURRENT_DIR"/../scripts/dataset-import/dump-for-migrations-core-0004-tournesol-0007.sql.tgz
sudo mv dump.sql "$CURRENT_DIR"/data/db/
sudo chown 999:999 "$CURRENT_DIR"/data/db/dump.sql
docker exec --env PGPASSWORD=password tournesol-dev-db bash -c "psql -1 -q -d tournesol -U user < /var/lib/postgresql/data/dump.sql"
sudo rm "$CURRENT_DIR"/data/db/dump.sql

echo 'Creating Superuser:'
# docker exec -ti dev-env_web_1 python manage.py createsuperuser
USERNAME="${1:-"$USER"}"
PASSWORD="${2:-"yop"}"
EMAIL="${3:-"$USER@kleis.ch"}"
"$CURRENT_DIR/create-superuser-local.exp" "$USERNAME" "$PASSWORD" "$EMAIL"

echo 'Creating OAuth Application:'
# OAUTH_CLIENT_ID="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)" || true
# OAUTH_CLIENT_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)" || true
OAUTH_CLIENT_ID="YlfkLzvVjmGw3gjJzdlFuMFWcR64fAk4WNg5ucGg"
OAUTH_CLIENT_SECRET="iB9j9hM5ekFpKlZQ6uNGloFJIWLVnq8LoG7SNdCtHY5oM7w9KY0XjpaDuwwJ40BshH7jKYZmXniaybhrQf5p4irAOMWv82RdYRMD6TTSJciZEAxn9onpKQoUgUeDqsRj"
now="$(date +%Y-%m-%d)"
docker exec --env PGPASSWORD=password tournesol-dev-db bash -c "psql -d tournesol -U user <<< \"insert into oauth2_provider_application (client_id, redirect_uris, client_type, authorization_grant_type, client_secret, name, skip_authorization, algorithm, created, updated) values ('$OAUTH_CLIENT_ID', 'http://localhost:8000/admin/', 'confidential', 'password', '$OAUTH_CLIENT_SECRET','Frontend', true, 'RS256', '$now', '$now');\""

echo 'Creating Swagger UI OAuth Application:'
# OAUTH_CLIENT_ID="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)" || true
# OAUTH_CLIENT_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)" || true
OAUTH_CLIENT_ID="vY17xBi0MZKZCotrfma5ympAd0hq30OudU78HZAY"
OAUTH_CLIENT_SECRET="ZJ5FZeHomIgq6uNpVgNKwJiXDfFZz1HijDhsQJlXXnFKF6R7bUqc49Dv5MNL3cYTUrE1axrTtJTSr6IkHCc417ye8bLR8facpmhD4TwQqg7ktIQ047Y2Xp0rRcKLlIvq"
now="$(date +%Y-%m-%d)"
docker exec --env PGPASSWORD=password tournesol-dev-db bash -c "psql -d tournesol -U user <<< \"insert into oauth2_provider_application (client_id, redirect_uris, client_type, authorization_grant_type, client_secret, name, skip_authorization, algorithm, created, updated) values ('$OAUTH_CLIENT_ID', 'http://localhost:8000/docs/', 'confidential', 'password', '$OAUTH_CLIENT_SECRET','Swagger UI', true, 'RS256', '$now', '$now');\""

echo 'Launching Django:'
python manage.py runserver 127.0.0.1:8000

# rm "$CURRENT_DIR/settings-tournesol-local.yaml"
